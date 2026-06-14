def register(api):
    def run(ctx):
        resp = ctx.fetch('https://example.com')
        ctx.announce('status:' + str(resp['status']))
    api.register_command('run', run)
