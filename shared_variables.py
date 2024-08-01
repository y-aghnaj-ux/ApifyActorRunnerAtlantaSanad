default_token = "apify_api_HHHGW1cu1T1NdtyhdfKZNjZ1OKxsAb09U30J"
default_token_list = ["apify_api_HHHGW1cu1T1NdtyhdfKZNjZ1OKxsAb09U30J","apify_api_t6keq5nqZlewnVPJeC48seYUtPm6xP1yfzAh"]
if default_token not in default_token_list:
    default_token_list.append(default_token)

theme = "blue"
appearance = "Light"
background = "white"
output_folder_path = ""
foreground="#939BA2"

def ChangeAppearance(appearance_name):
    global appearance, background,foreground
    match appearance_name:
        case "Light":
            appearance = "light"
            background = "#FFFFFF"
            foreground = "#939BA2"
        case "Dark":
            appearance = "dark"
            background = "#242424"
            foreground = "#4A4D50"



def ChangeTheme(theme_name):
    global theme
    match theme_name:
        case "Dark Red":
            theme = "dark_red.json"
        case "Dark Blue":
            theme = "dark-blue"
        case "Blue":
            theme = "blue"
        case "Green":
            theme = "green"
        case "Yellow":
            theme = "yellow.json"
        case "Rainbow":
            theme = "rainbow.json"
    print(f"Theme changed to: {theme}")
