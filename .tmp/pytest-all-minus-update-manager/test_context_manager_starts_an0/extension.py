def register(api):
    def run(ctx):
        ctx.insert_text('hi')
    api.register_command('run', run)
