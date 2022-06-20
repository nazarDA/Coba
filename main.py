import pandas as pd
# Bokeh libraries
from bokeh.plotting import figure, show
from bokeh.io import output_file
from bokeh.models import ColumnDataSource, CDSView, GroupFilter, HoverTool,NumeralTickFormatter
from bokeh.layouts import column, row
from bokeh.models.widgets import Tabs, Panel
from bokeh.io import curdoc
from os.path import dirname, join

# Membaca file dataset berupa file csv
player_stats = pd.read_csv(join(dirname(__file__), 'data','2017-18_playerBoxScore.csv'), parse_dates=['gmDate'])
team_stats = pd.read_csv(join(dirname(__file__), 'data','2017-18_teamBoxScore.csv'), parse_dates=['gmDate'])
standings = pd.read_csv(join(dirname(__file__), 'data','2017-18_standings.csv'), parse_dates=['stDate'])

# Memasukkan hasil baca file csv ke ColumnDataSource
standings_cds = ColumnDataSource(standings)

# Membuat view berdasarkan dengan source ColumnDataSource
celtics_view = CDSView(source=standings_cds,
                      filters=[GroupFilter(column_name='teamAbbr', 
                                           group='BOS')])

raptors_view = CDSView(source=standings_cds,
                      filters=[GroupFilter(column_name='teamAbbr', 
                                           group='TOR')])

rockets_view = CDSView(source=standings_cds,
                      filters=[GroupFilter(column_name='teamAbbr', 
                                           group='HOU')])
warriors_view = CDSView(source=standings_cds,
                      filters=[GroupFilter(column_name='teamAbbr', 
                                           group='GS')])

# Mencari pemain yang setidaknya melakukan tembakan 3 angka 1 kali
three_takers = player_stats[player_stats['play3PA'] > 0]

# memasukkan nama pemain ke satu kolom
three_takers['name'] = [f'{p["playFNm"]} {p["playLNm"]}' 
                        for _, p in three_takers.iterrows()]

# mengagregasi total percobaan tembakan 3 angka tiap pemain
three_takers = (three_takers.groupby('name')
                            .sum()
                            .loc[:,['play3PA', 'play3PM']]
                            .sort_values('play3PA', ascending=False))

# melakukan penyaringan pemain mana saja yang tidak melakukan setidaknya 100 kali percobaan tembakan 3 angka dalam musim 2017/2018
three_takers = three_takers[three_takers['play3PA'] >= 100].reset_index()

# menambah kolom presentase tembakan 3 angka
three_takers['pct3PM'] = three_takers['play3PM'] / three_takers['play3PA']

# menyimpan data ke dalam ColumnDataSource
three_takers_cds = ColumnDataSource(three_takers)

# Membuat plot dengan view yang telah dibuat
east_fig = figure(x_axis_type='datetime',
                  plot_height=300,
                  x_axis_label='Date',
                  y_axis_label='Wins',
                  toolbar_location=None,
                  title="Win Race from Top 2 Seed Eastern Conference 2017/2018 NBA Season")

west_fig = figure(x_axis_type='datetime',
                  plot_height=300,
                  x_axis_label='Date',
                  y_axis_label='Wins',
                  toolbar_location=None,
                  title="Win Race from Top 2 Seed Western Conference 2017/2018 NBA Season")


east_fig.step('stDate', 'gameWon', 
              color='#007A33', legend='Celtics',
              source=standings_cds, view=celtics_view)
east_fig.step('stDate', 'gameWon', 
              color='#CE1141', legend='Raptors',
              source=standings_cds, view=raptors_view)

west_fig.step('stDate', 'gameWon', color='#CE1141', legend='Rockets',
              source=standings_cds, view=rockets_view)
west_fig.step('stDate', 'gameWon', color='#006BB6', legend='Warriors',
              source=standings_cds, view=warriors_view)

# Memvisualisasikan legend tiap plot di posisi kiri atas
east_fig.legend.location = 'top_left'
west_fig.legend.location = 'top_left'

# Mengatur lebar plot
east_fig.plot_width = west_fig.plot_width = 800

# Membuat 2 panel untuk masing-masing wilayah liga
east_panel = Panel(child=east_fig, title='Eastern Conference')
west_panel = Panel(child=west_fig, title='Western Conference')

# membuat Tabs untuk menampung panel yang dibuat
tabs = Tabs(tabs=[west_panel, east_panel])

select_tools = ['box_select', 'lasso_select', 'poly_select', 'tap', 'reset']

# membuat plot
threept_fig = figure(plot_height=400,
             plot_width=600,
             x_axis_label='Three-Point Shots Attempted',
             y_axis_label='Percentage Made',
             title='3PT Shots Attempted vs. Percentage Made (min. 100 3PA), 2017-18 NBA Season',
             toolbar_location='below',
             tools=select_tools)

threept_fig.yaxis[0].formatter = NumeralTickFormatter(format='00.0%')

threept_fig.square(x='play3PA',
           y='pct3PM',
           source=three_takers_cds,
           color='royalblue',
           selection_color='deepskyblue',
           nonselection_color='lightgray',
           nonselection_alpha=0.3)

# Membuat format untuk hover
tooltips = [
            ('Player','@name'),
            ('Three-Pointers Made', '@play3PM'),
            ('Three-Pointers Attempted', '@play3PA'),
            ('Three-Point Percentage','@pct3PM{00.0%}'),
           ]

# membuat pengaturan hover
hover_glyph = threept_fig.circle(x='play3PA', y='pct3PM', source=three_takers_cds,
                         size=15, alpha=0,
                         hover_fill_color='black', hover_alpha=0.5)

# menambahkan HoverTool ke plot
threept_fig.add_tools(HoverTool(tooltips=tooltips, renderers=[hover_glyph]))

layout = column(tabs,threept_fig)

# Visualisasi Data
curdoc().title = "Interactive Data Visualization on 2017/2018 NBA Season"
curdoc().add_root(layout)