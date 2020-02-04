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