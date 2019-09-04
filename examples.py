from chart_session import ChartSession

def ex1():
  with ChartSession() as session:
    figure = session.get_figure()
    plot1 = figure.get_new_plot()
    plot1.set_label("blue line")
    plot1.plot([0,2,4,6,8], [5,7,3,4.3,2], linecolor="#0000ff")

    plot2 = figure.get_new_plot()
    plot2.set_label("red line")
    plot2.plot([0,2,4,6,8], [1,2,3,4,6], linecolor="#ff0000")
    figure.get_legend().set_display(True)
    ip = figure.add_interactive_plot()
    figure.set_title("Plot")
    session.show(blocking=True)

def ex2():
  with ChartSession() as session:
    figure = session.get_figure()
    plot1 = figure.get_new_plot()
    plot1.set_label("blue line")
    plot1.plot([0,2,4,6,8], [5,7,3,4.3,2], linecolor="#0000ff")

    plot2 = figure.get_new_plot()
    plot2.set_label("red line")
    plot2.plot([0,2,4,6,8], [1,2,3,4,6], linecolor="#ff0000")
    figure.get_legend().set_display(True)
    session.set_figure_size(1200, 700)
    figure.set_title("Plot")

    session.show(blocking=False)
    session.save("file.png")

def ex3():
  with ChartSession() as session:
    figure = session.get_figure()
    plot = figure.get_new_plot()
    plot.scatter([0,2,4,6,8], [5,7,3,4,2], labels=["a","b","c","d","e"])
    figure.set_title("test-title")
    session.show()

if __name__ == "__main__":
    ex1()
    ex2()
    ex3()
