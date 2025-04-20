import streamlit as st
from streamlit_option_menu import option_menu

# Sidebar içine menüyü yerleştiriyoruz
with st.sidebar:
    selected = option_menu(
        menu_title="🎵 Music to Movie",  # Menü başlığı
        options=["Home", "Developer Mode", "Settings", "Logout"],  # Sekmeler
        icons=["house", "code-slash", "gear", "box-arrow-right"],  # Bootstrap ikonları
        menu_icon="cast",  # Menü başı ikonu
        default_index=0,  # Başlangıçta seçili olan
    )

# İçeriği seçime göre değiştir
if selected == "Home":
    st.title("🏠 Ana Sayfa")
    st.write("Burası ana içerik.")
elif selected == "Developer Mode":
    st.title("💻 Geliştirici Modu")
    st.code("print('Hello dev!')")
elif selected == "Settings":
    st.title("⚙️ Ayarlar")
    st.write("Tema, kullanıcı bilgileri vb.")
elif selected == "Logout":
    st.warning("🔒 Oturum kapatılıyor...")

selected = option_menu(
    menu_title=None,  # Üst bar için başlık gösterilmez
    options=["🎧 Şarkılar", "🎬 Filmler", "📊 İstatistik", "⚙️ Ayarlar"],
    icons=["music-note", "film", "bar-chart", "gear"],
    orientation="horizontal",
)

st.write(f"Seçilen sekme: {selected}")