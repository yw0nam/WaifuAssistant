# Conventional Commits Guide

All commit messages in this repository must adhere to the Conventional Commits specification. This allows for a more readable history and automated versioning.

## Commit Message Format

Each commit message consists of a **header**, a **body**, and a **footer**.

```
<type>[optional scope]: <subject>
<BLANK LINE>
[optional body]
<BLANK LINE>
[optional footer(s)]
```

### Header

The header is mandatory and includes:

- **type**: Describes the kind of change that you're committing.
- **scope** (optional): A noun describing a section of the codebase surrounded by parentheses. e.g., `(api)`, `(ui)`.
- **subject**: A short, imperative-tense description of the change.

### Body (Optional)

The body is used to provide additional context, explaining the *what* and *why* of the change.

### Footer (Optional)

The footer is used to reference issue tracker IDs or to denote a **BREAKING CHANGE**.

---

## Types

### Main Types

- `feat`: A new feature for the user. (**bumps MINOR version**)
- `fix`: A bug fix for the user. (**bumps PATCH version**)

### Other Types

- `docs`: Changes to documentation only.
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc).
- `refactor`: A code change that neither fixes a bug nor adds a feature.
- `perf`: A code change that improves performance.
- `test`: Adding missing tests or correcting existing tests.
- `build`: Changes that affect the build system or external dependencies.
- `ci`: Changes to our CI configuration files and scripts.
- `chore`: Other changes that don't modify `src` or `test` files.

---

## Breaking Changes

A commit that introduces a breaking API change **MUST** be noted by appending a `!` after the type/scope, or by adding `BREAKING CHANGE:` in the footer. This type of commit will bump the **MAJOR version**.

**Example 1: Using `!`**

```
feat(api)!: drop support for Node 8
```

**Example 2: Using the footer**

```
refactor: rename user model to customer

BREAKING CHANGE: The `User` model has been renamed to `Customer`. Any part of the application that referenced the old model must be updated.
```