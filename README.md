# mini_c_compiler
> Practicing project inspired by [one of Destroy All Software screencasts](https://www.destroyallsoftware.com/screencasts/catalog/a-compiler-from-scratch)

## Basic Components
- Tokenizer (Lexer or whatever)
  - Turn input code (string) into tokens with basic categorization
  - Regular expression should be capable to finish this job.
  - Trying to follow grammars from [C (programming language)](https://en.wikipedia.org/wiki/C_(programming_language))
- Parser
  - Turn input tokens into syntax tree
  - Need context free mechanism to finish this job
- Validation
  - Do static analysis on parsed syntax tree
  - Should be able to do type check & optimizaitons
- Code Generator (Not there yet)
  - Turn input tree into executable code (literally any kind of code, preferably assembly)
- Interpreter:
  - Traverse syntax tree and evaluate the execution, like a C language "VM"
  - Easier to implement than code generator

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

Run interpreter against target code file:
- target code:
```
int newton(int x, int iter) {
    int i = 0;
    int z = 1;
    while(i < iter) {
        z -= (z*z - x) / (2*z);
        i++;
    }
    return z;
}

int main() {
    int input = 200000000;
    int iter = 30;
    return newton(input, iter);
}
```
Interpretation: 
```
$ python3 src/interpreter.py test_files/newton_sqrt.c
14143
```

## Reference
- [A Compiler From Scratch](https://www.destroyallsoftware.com/screencasts/catalog/a-compiler-from-scratch)
- [Chomsky Hierarchy](https://en.wikipedia.org/wiki/Chomsky_hierarchy)
