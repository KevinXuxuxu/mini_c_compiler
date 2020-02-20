int main() {
    int a[] = {13242,234,123,111,42,34,23,42,34,23,4234123,41234,234,32,42,1234,0};
    int n = 17;
    int i = n - 1;
    while(i > 0) {
        int j = 0;
        while(j < i) {
            if (a[j] < a[j+1]) {
                int tmp = a[j];
                a[j] = a[j+1];
                a[j+1] = tmp;
            }
            j++;
        }
        i--;
    }
    i = 0;
    while(i < n) {
        printf("%d\n", a[i]);
        i++;
    }
    return 0;
}