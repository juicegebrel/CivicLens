# Contributing to CivicLens

## Commit messages
This project uses [Conventional Commits](https://www.conventionalcommits.org/).

```
<type>(<optional scope>): <short description>

<optional body: what and why>

<optional footer: BREAKING CHANGE: ..., Closes #12>
```

**Types**

| Type | Use for |
|---|---|
| `feat` | a new feature or screen |
| `fix` | a bug fix |
| `docs` | documentation only |
| `style` | formatting, CSS tweaks with no behaviour change |
| `refactor` | code change that neither fixes a bug nor adds a feature |
| `perf` | performance improvement |
| `test` | adding or fixing tests |
| `build` | dependencies, packaging, settings |
| `ci` | CI configuration |
| `chore` | maintenance such as `.gitignore` |
| `revert` | reverting an earlier commit |

**Scopes** match the app or area: `accounts`, `config`, `dashboard`, `projects`, `statuscheck`, `ui`.

Use the imperative mood ("add", not "added"), keep the first line under 72 characters, and mark breaking changes with `!` (for example `feat(projects)!: rename status codes`).

Examples:
```
feat(statuscheck): show last update date on result card
fix(accounts): block barangay users from editing other barangays
docs: explain deployment settings
```

## Enforce it locally
A `commit-msg` hook that rejects non-conforming messages is included. Enable it once per clone:

```
git config core.hooksPath .githooks
```

On macOS/Linux, also run `chmod +x .githooks/commit-msg` if the file is not executable.

## Branches
Branch from `main` using `<type>/<short-name>`, for example `feat/barangay-report` or `fix/login-redirect`.
