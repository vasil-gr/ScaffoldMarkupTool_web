import streamlit as st
from app_pages.markup import markup
from app_pages.analysis import analysis
from app_pages.help import help

pg = st.navigation([
    st.Page(markup, title="Markup", icon=""),
    st.Page(analysis, title="Analysis", icon=""),
    st.Page(help, title="Help", icon=""),
])
pg.run()