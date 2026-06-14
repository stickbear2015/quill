def register(api):
    def run(ctx):
        ctx.log('diagnostic only')
        ctx.announce('user message')
    api.register_command('run', run)
