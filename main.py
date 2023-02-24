from bs4 import BeautifulSoup
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

import pandas as pd
import streamlit as st
import httpx
import io
import re

st.set_page_config(
    page_title="Scrape Google Scholar - Ivan Masyudi",
    page_icon="🔎"
)

st.markdown(
    """
    <style>
    #MainMenu{
        visibility:hidden;
    }
    </style>
    """, unsafe_allow_html=True
)
data_dict = {'Penulis':[],
             'Tahun':[], 
            'Judul':[], 
            'Sitasi':[],
            'URL Dokumen':[], 
            'Konferens/Jurnal/Buku':[], 
            'Nama Penulis 1':[],
            'Asal Penulis 1':[],
            'Nama Penulis 2':[],
            'Asal Penulis 2':[],
            'Nama Penulis 3':[],
            'Asal Penulis 3':[],
            'Nama Penulis 4':[],
            'Asal Penulis 4':[],
            'Nama Penulis 5':[],
            'Asal Penulis 5':[],
            'Nama Penulis 6':[],
            'Asal Penulis 6':[],
            'Nama Penulis 7':[],
            'Asal Penulis 7':[]
            }

st.title("🔎 Scraping Google Scholar")
with st.expander("⚠️ Tutorial Penggunaan"):
    st.warning(
        """
        **NOTE:** \n
        Website ini hanya bisa scraping data pada Google Scholar. Data penulis
        yang dapat diambil hanya 7 penulis. Jika lebih maka sistem akan error.
        \n
        📢 Untuk mengambil seluruh data penelitian lengkap yang lebih dari 20 halaman. Silahkan copy
        text dibawah ini dan letakkkan dipaling akhir setelah url.  
        """
        )
    
    st.success(
        """
        &cstart=0&pagesize=500
        """
        )
    

with st.form("myform"):
    penulis = st.text_input("Penulis", placeholder="Masukkan Nama Penulis")
    linkurl = st.text_input("URL", placeholder="Masukkan URL")


    if "scrape_state" not in st.session_state:
        st.session_state.scrape_state = False
    
    submit_button = st.form_submit_button(label='Submit')

if submit_button or st.session_state.scrape_state and linkurl != "":
    st.session_state.scrape_state = True
    data_dict['Penulis'].append(penulis)
    file_name = re.sub(r'[\W\s_]',' ', penulis)

    req = httpx.get(linkurl)
    st.write(req)
    print(req)

    soup = BeautifulSoup(req.text, 'html.parser')

    items = soup.findAll('tr', class_='gsc_a_tr')
    for reviews in items:

        tahun = reviews.find('span', class_='gsc_a_h gsc_a_hc gs_ibl').text
        data_dict['Tahun'].append(tahun)

        judul = reviews.find('a', class_='gsc_a_at').text
        data_dict['Judul'].append(judul)

        sitasi = reviews.find('a', class_='gsc_a_ac gs_ibl').text
        data_dict['Sitasi'].append(sitasi)

        np = reviews.find('div', class_='gs_gray').text
        listnp = np.split(", ")
        if len(listnp) < 7:
            step = 7 - len(listnp)
            for j in range(step):
                listnp.append("None")

        for j in range(len(listnp)):
            data_dict[f'Nama Penulis {j+1}'].append(listnp[j])

    df = pd.DataFrame.from_dict(data_dict, orient='index')
    df = df.transpose()

    gd = GridOptionsBuilder.from_dataframe(df)
    gd.configure_pagination(enabled=True)
    gd.configure_default_column(editable=True)
    gridoption = gd.build()
    AgGrid(df, gridOptions=gridoption)

    # Konversi DataFrame ke Excel dan simpan di buffer
    buffer = io.BytesIO()
    writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    excel_data = buffer.getvalue()

    # Tampilkan button download
    st.download_button(
        label='Download Excel',
        data=excel_data,
        file_name=f'{file_name}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
