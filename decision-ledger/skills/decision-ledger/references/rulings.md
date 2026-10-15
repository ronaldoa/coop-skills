# Rulings: format, placement, overturning

## Format

```
⚖️ user <YYYY-MM-DD> "<verbatim quote, original language>"
  — decides: <what is now settled, one sentence>
  — overturns: <the earlier text/ruling it replaces, with its pointer>   (if any)
  — closes: <Qn>                                                          (if any)
  — options it answered: <only when the quote is "A" / "同意" / "go ahead">
```

A paraphrase is a mirror, and the clause it drops is the load-bearing one — when acting on
a ruling later, re-read the quote, not your summary. One message answering several
questions = one record per question, same quote.

## Placement — one home, pointers elsewhere

| Scope | Home |
|---|---|
| one open question | its entry: `### Qn [RULED <date>]` |
| one line of work | that line doc's `§0.1`, or inline at the rule it changes |
| cross-cutting, every session | the router's standing rules, with the date and the motivating incident; the router's line ceiling applies |
| a debt's disposition | the debt entry |

Standing-rule form: `- **<rule>.** (User ruling 2026-08-03: "<quote>".)` — and when the rule
gains a mechanical guard, the line names the test.

## Overturning

Record the new ruling with `overturns:`; mark the old text `[SUPERSEDED <date> → <pointer>]`
and leave it in place; sweep every citation of the old one (the gate only catches
`Qn (open)`; other citations need a grep). Never edit an old ruling's text to match today.

## Commit form

`⚖️ <what was decided> (⚖️ user 2026-10-14 "<quote>"; zero LLM, zero code)` — then
`git log --oneline --grep=⚖️` is the ruling history.

## Not a ruling

- an agent recommendation the user did not object to;
- a ruling from another line or session applied by analogy — ask;
- permission for the next similar act: spending, deleting, pushing are ruled per occasion
  unless the ruling says otherwise in words.
