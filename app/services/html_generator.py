from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("app/templates"))

def generar_html(course_data):
    template = env.get_template("course.html")
    return template.render(**course_data)