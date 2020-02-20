int newton(int v, int target, int i) {
    if (i == 0)
        return v;
    return newton(v-(v*v - target) / (2*v), target, i-1);
}

int main() {
    return newton(1, 200000000, 30);
}
