def register(api):
    def run(ctx):
        try:
            ctx.read_file('C:/secret.txt')
            ctx.announce('LEAKED')
        except Exception as exc:
            ctx.announce('denied:' + type(exc).__name__)
    api.register_command('run', run)
