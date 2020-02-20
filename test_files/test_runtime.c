int print_to(int n) {
    int i = 0;
    while(i < n) {
        printf("we have %d\n", i);
        i++;
    }
    return i;
}

int main() {
    return print_to(5);
}