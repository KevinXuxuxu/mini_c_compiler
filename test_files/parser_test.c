/* bool test_func(int a=NULL, bool b=false, char c='\n') {
    1+!(++a--+(++b))*5 + call1(12, a*(c+call2(!b)), r) * 3
}
*/
/*
bool test_func() {
    a = 12*3 + sqrt(a * (b+c));
    int q = p++;
    int plus(int a, int b) {
        a+b;
    }
    return exp(a()+!--b);
    call(12, 45%++b);
    return;
} */

/*
int plus(int a, int b) {
    return a+b;
}

bool test_func(int a, bool b) {
    int c = plus(12*(1+4), a);
    a += 12 * c % 5;

    bool func2(bool x, bool y) {
        int c = 2;
        return (x || y ) && b;
    }

    // return !func2(b, b);
}
*/

/*
int get_max(int a, int b) {
    if (a > b) {
        a += 12 * get_max(a, a*b);
        if (a <=b + 34)
            return a;
        else if (a != b)
            return a - get_max(1,4);
    } else return b;
}
*/

/*
int max(int a, int b) {
    if (a > b)
        return a;
    return b;
}
*/

int test() {
    int i = 0;
    while(i < 10) {
        i++;
    }
    while (i > -2)
        if (i == 0)
            return i;
}