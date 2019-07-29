def hello(request):
    name = request.args['name'] if request.args and 'name' in request.args else 'world'
    return r'<b>Hello {}</b>'.format(name)
