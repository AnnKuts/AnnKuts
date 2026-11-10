from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/yourtomo')


def replace_once(text: str, old: str, new: str, filename: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{filename}: expected one match, found {count}: {old[:80]}')
    return text.replace(old, new, 1)


def patch(path: Path, replacements: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding='utf-8')
    for old, new in replacements:
        text = replace_once(text, old, new, str(path))
    path.write_text(text, encoding='utf-8')


for filename in ('render.ts', 'graphRender.ts', 'isoRender.ts'):
    patch(root / 'src' / filename, [
        ('body: "#e6edf3"', 'body: "#f28c38"'),
        ('body: "#1f2328"', 'body: "#d97721"'),
    ])

patch(root / 'src' / 'state.ts', [
    (
        'const where = name ? `welcome to ${name}\'s corner` : "welcome to my corner";',
        'const where = name ? `${name} codes, Symon supervises` : "Symon supervises";',
    ),
])

patch(root / 'src' / 'render.ts', [
    ('scroll down for projects + contact', 'scroll down, my human made stuff'),
    (
        'if (hackingOn) hints.push(`hacking on ${hackingOn}`);',
        'if (hackingOn) hints.push(`my human works on ${hackingOn}`);',
    ),
    (
        'hints.push("featured projects ↓", "live stats + graphs ↓");',
        'hints.push("check out her projects ↓", "numbers and nerdy stuff ↓");',
    ),
    (
        'if (contact) hints.push(`say hi: ${contact}`);',
        'if (contact) hints.push(`find Anna: ${contact}`);',
    ),
    ('dreaming in ${esc(topLang)}', 'dreaming of ${esc(topLang)} snacks'),
])

patch(root / 'generate.ts', [
    (
        'status = applyForceState(status, process.env.PET_FORCE_STATE || "");',
        '''status = applyForceState(status, process.env.PET_FORCE_STATE || "");

    const symonLines: Record<string, string> = {
        zoomies: "Symon.exe is chasing bugs!",
        sleeping: "Symon is sleeping. Shhh...",
        content: "Symon approves this code. Probably.",
        hungry: "No commits? No treats!",
        grumpy: "Symon is judging your code.",
        release: "New release! Where are my treats?",
        overheat: "The CI is on fire. Meow.",
        sick: "Too many issues. Send help.",
        hibernating: "Symon is on vacation.",
    };

    status.caption = symonLines[status.state] ?? status.caption;''',
    ),
])

api = root / 'src' / 'githubApi.ts'
code = api.read_text(encoding='utf-8')
start = code.index('export async function fetchRepos(')
langs_start = code.index('export async function fetchLanguages(', start)
langs_end = code.index('// repos whose CI', langs_start)
repos = code[start:langs_start]
langs = code[langs_start:langs_end]

repos = replace_once(
    repos,
    'if (token()) attempts.push(["/user/repos?per_page=100&affiliation=owner&visibility=public", true]);',
    'if (token()) attempts.push([`/users/${user}/repos?per_page=100&type=owner`, true]);',
    'fetchRepos',
)
repos = replace_once(
    repos,
    'if (isAuthFailure(err)) return [];',
    'if (isAuthFailure(err)) continue;',
    'fetchRepos',
)
langs = replace_once(
    langs,
    'if (isAuthFailure(err)) return null;',
    'if (isAuthFailure(err)) continue;',
    'fetchLanguages',
)
api.write_text(code[:start] + repos + langs + code[langs_end:], encoding='utf-8')
print('Symon personalized; GitHub public-stats fallback enabled.')
