def register(api):
    def run(ctx):
        raise RuntimeError('boom')
    api.register_command('run', run)
