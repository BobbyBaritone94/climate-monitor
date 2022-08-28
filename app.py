from pydoc import classname
import dash  # pip install dash
import dash_labs as dl  # pip install dash-labs
import dash_bootstrap_components as dbc # pip install dash-bootstrap-components
from dash import html, html
from dash_bootstrap_templates import ThemeSwitchAIO #pip install dash-bootstrap-templates
# Code from: https://github.com/plotly/dash-labs/tree/main/docs/demos/multi_page_example1

template_theme1 = "flatly"
template_theme2 = "darkly"
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY

dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css"
)
app = dash.Dash(
    __name__, plugins=[dl.plugins.pages], external_stylesheets=[dbc.themes.BOOTSTRAP]
)
server=app.server

navbar = dbc.Navbar(
    [
        html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src='assets/FIU-Logo.png', height="30px")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="https://plotly.com",
                style={
                    "textDecoration": "none",
                    "margin-left":"30px"
                },
                ),
        html.Div(
            ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2],),
            className="darkMode"
        ),
        dbc.Container(
            [
                dbc.NavItem(dbc.NavLink(page["name"], href=page["path"],className='navLinks'))
                for page in dash.page_registry.values()
                if page["module"] != "pages.not_found_404"
                # dbc.DropdownMenu(
                #     [
                #         dbc.DropdownMenuItem(page["name"], href=page["path"])
                #         for page in dash.page_registry.values()
                #         if page["module"] != "pages.not_found_404"
                #     ],
                #     nav=True,
                #     in_navbar=True,
                #     id="navbarTogglerDemo02",
                #     label="More",
                #     style={
                #         'marginRight':'80px'
                #     }
                # ),
                
            ],
            style={
                'display':'flex',
                'justify-content':'right'
            }
        ),
    ],
    color="#071F3F",
    dark=True,
    # class_name='navbar navbar-expand-lg navbar-light bg-light'
)




app.layout = dbc.Container(
    [navbar, dl.plugins.page_container],
    fluid=True,
    style={
        'margin':'0',
    }
)

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0',port=5000)