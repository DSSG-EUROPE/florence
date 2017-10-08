
# todo: fix plot_timeseries_button_plot module
# def plot_timeseries_button_plot(df, museum_list, timedelta='hour', plotname='timeseries'):

#     """
#     Plots button plot of timeseries for a given timedelta
#     """

#     dates = df.date.unique()

#     dataPanda = []

#     # for n in range(1, len(museum_list)):
#     #     for museum in museum_list:
#     #         trace = go.Bar(x=df[museum][timedelta],
#     #                        y=df[museum].total_entries,
#     #                        name=museum,
#     #                        visible=True,
#     #                        marker=Marker(
#     #                            color='#CC171D',  # set bar colors
#     #                        ))
#     #
#     #
#     #         # args = [True, False, False, False, False, False, False, False, False, False, False,
#     #         #                                      False, False, False, False, False, False, False, False, False, False, False,
#     #         #                                      False, False, False, False, False, False, False, False, False, False, False,
#     #         #                                      False, False, False, False, False, False, False, False]


#     data = dataPanda

#     updatemenus = list([
#         dict(type="dropdown",
#              active=0,
#              buttons=list([menusdict]),
#              direction='down',
#              showactive=True,
#              x=1,
#              xanchor='top',
#              y=1,
#              yanchor='top'
#              )
#     ])

#     layout = go.Layout(
#         showlegend=False,
#         autosize=False,
#         updatemenus=updatemenus,
#         width=900,
#         height=500,
#         paper_bgcolor='#ffffff',
#         plot_bgcolor='#ffffff',
#         barmode='group',
#     )

#     fig = dict(data=data, layout=layout)
#     plot_url = py.iplot(fig, filename=plotname, sharing='private')

#     return df, plot_url


# def make_html(name='helloworld.html', plotlst='plot_url'):
#
#     """
#     Small function that generates html file from input plots
#     """
#
#     to_plot = plotlst.keys()
#
#     import plotly.tools as tls
#     Html_file = open(name, "w")
#
#     p1 = tls.get_embed(to_plot)
#     Html_file.write(p1)
#     Html_file.close()

