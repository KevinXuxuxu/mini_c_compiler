# mini_c_compiler
> Practicing project inspired by [one of Destroy All Software screencasts](https://www.destroyallsoftware.com/screencasts/catalog/a-compiler-from-scratch)

## Basic Components
- Tokenizer (Lexer or whatever)
  - Turn input code (string) into tokens with basic categorization
  - Regular expression should be capable to finish this job.
  - Trying to follow grammars from [C (programming language)](https://en.wikipedia.org/wiki/C_(programming_language))
- Parser
  - Turn input tokens into syntax tree
  - Should be able to do type check & optimizaitons
  - Need context free mechanism to finish this job
- Code Generator (Not there yet)
  - Turn input tree into executable code (literally any kind of code, preferably assembly)

## Reference
- [A Compiler From Scratch](https://www.destroyallsoftware.com/screencasts/catalog/a-compiler-from-scratch)
- [Chomsky Hierarchy](https://en.wikipedia.org/wiki/Chomsky_hierarchy)
