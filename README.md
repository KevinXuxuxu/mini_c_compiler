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

## Usage
Run compiler against target code file:
```
$ python3 src/compiler.py test_files/parser_test
(token list)
[M_COMMENT]('/* bool test_func(int a=NULL, bool b=false, char c='\n') {
    1+!(++a--+(++b))*5 + call1(12, a*(c+call2(!b)), r) * 3
}
*/')
...
[NAME]('a')
[COMMA](',')
[BASE_TYPE]('int')
[NAME]('b')
[C_PAREN](), None, None)
[O_BRAC]('{')
[IF]('if')
...
(syntax tree)
Root:
   functions:
   - FuncDef:
      type: 'int'
      name: 'get_max'
      args:
      - VarDef:
         name: 'a'
         type: 'int'
         default: None
      - VarDef:
         name: 'b'
         type: 'int'
         default: None
      body:Block:
         statements:
         - If:
            ...
```
Compiler errors will be raised as exceptions.

## Reference
- [A Compiler From Scratch](https://www.destroyallsoftware.com/screencasts/catalog/a-compiler-from-scratch)
- [Chomsky Hierarchy](https://en.wikipedia.org/wiki/Chomsky_hierarchy)
