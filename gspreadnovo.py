import gspread
#Autenticação
gc = gspread.service_account(filename='credentials.json')
#Abrir a planilha principal
sh= gc.open_by_key("16tjePCI2QMaMIOLIFVNYjcM7A2UFHYpt6DZ-sk6hioo")
#Obter lista das planilhas
worksheet_list = sh.worksheets()
#Todas as planilhas disponiveis
print(worksheet_list)
#Selecionar a planilha que quero
worksheet = sh.worksheet("Cambones")
#Obter um valor da planilha
# worksheet.update('OIOI','B20')