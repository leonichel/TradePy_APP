mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"leonichelg@gmail.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
[theme]\n\
primaryColor='#ff5555'\n\
backgroundColor='#282a36'\n\
secondaryBackgroundColor='#44475a'\n\
textColor='#f8f8f2'\n\
font='sans serif'\n\
" > ~/.streamlit/config.toml