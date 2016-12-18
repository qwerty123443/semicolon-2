"""Server settings cog."""
import os
import gearbox
cog = gearbox.Cog()
_ = cog.gettext
ngettext = cog.ngettext


DEFAULT_PREFIX = ';'


@cog.command(permissions='manage_server')
def prefix(server_ex, command: {'get', 'add', 'del', 'reset'}='get', *args):
    """Display or change prefix settings for the current server.

    `get`: show prefixes, `add . ? !`: add prefixes, `del . ? !`: remove prefixes, `reset`: reset back to `;`"""
    command = command.lower()
    if command == 'get':
        if len(server_ex.prefixes) == 0:
            return _('This server has no prefix. Use `prefix add` to add some!')
        return ngettext("The prefix for this server is {prefixes}",
                        "The prefixes for this server are {prefixes}", len(server_ex.prefixes)).format(
            prefixes=gearbox.pretty(server_ex.prefixes, '`%s`', final=_('and')))
    elif command == 'add':
        if not args:
            return _('Please specify which prefix(es) should be added.')
        overlap = [pref for pref in args if pref in server_ex.prefixes]
        if overlap:
            return ngettext("{prefixes} is already used", "{prefixes} are already used", len(overlap)).format(
                prefixes=gearbox.pretty(overlap, '`%s`', final=_('and')))
        else:
            n = 0
            for pref in args:  # Not using .extend() in case of duplicates in args
                if pref not in server_ex.prefixes:
                    server_ex.prefixes.append(pref)
                    n += 1
            server_ex.write()
            return ngettext("Added {n} prefix.", "Added {n} prefixes.", n).format(n=n)
    elif command == 'del':
        if not args:
            return _('Please specify which prefix(es) should be deleted.')
        unused = [pref for pref in args if pref not in server_ex.prefixes]
        if unused:
            return ngettext("{prefixes} isn't used", "{prefixes} aren't used", len(unused)).format(
                prefixes=gearbox.pretty(unused, '`%s`', final=_('and')))
        else:
            n = 0
            for pref in args:
                if pref in server_ex.prefixes:
                    server_ex.prefixes.remove(pref)
                    n += 1
            server_ex.write()
            return ngettext("Removed {n} prefix.", "Removed {n} prefixes.", n).format(n=n)
    elif command == 'reset':
        server_ex.prefixes = [DEFAULT_PREFIX]
        server_ex.write()
        return _('Server prefix reset to `{default}`.').format(default=DEFAULT_PREFIX)


@cog.command(permissions='manage_server')
def breaker(server_ex, command: {'get', 'set'}='get', new_breaker=None):
    """Display or change breaker character for the current server."""
    command = command.lower()
    if command == 'get':
        return _("The breaker character for this server is `{breaker}`").format(breaker=server_ex.config['breaker'])
    elif command == 'set':
        if new_breaker is None:
            return _("Please use `set <breaker_character>`")
        if len(new_breaker) != 1:
            return _("The breaker character should be a single character")
        server_ex.config['breaker'] = new_breaker
        return _("The breaker character for this server has been set to `{breaker}`").format(breaker=new_breaker)


@cog.command(permissions='manage_server')
def lang(server_ex, language=None):
    """Display or change server language."""
    available_languages = os.listdir(gearbox.CFG['path']['locale'])
    try:  # Hide the 'templates' directory containing .pot files
        available_languages.remove('templates')
    except ValueError:
        pass
    if language is None or language not in available_languages:
        output = ''
        if language is None:
            output = _("Current server language: {language}").format(language=server_ex.config['language']) + "\n"
        output += (_('Available languages: {languages}').format(languages=gearbox.pretty(available_languages,
                                                                                         '`%s`', final=_('and'))) +
                   '\n' + _('Please note that full support is not guaranteed at all.'))
        return output
    else:
        server_ex.config['language'] = language
        server_ex.write()
        output = _("Server language has been set to `{language}`!").format(language=language)
        if '_' in language:
            output += f' :flag_{language.split("_")[-1].lower()}:'
        return output
