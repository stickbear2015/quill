def register(api):
    def run(ctx):
        ctx.replace_selection(ctx.get_selection().title())
        ctx.announce('done')
    api.register_command('run', run)
