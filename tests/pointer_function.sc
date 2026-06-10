void set_value(int *p, int value) {
    *p = value;
}

void add_one(int *p) {
    (*p)++;
}

int main() {
    int x;
    int *ptr;

    x = 5;
    ptr = &x;

    set_value(ptr, 20);
    printf("after set_value: x = %d\n", x);

    add_one(&x);
    printf("after add_one: x = %d\n", x);

    printf("ptr == &x : %d\n", ptr == &x);
    printf("ptr != 0 : %d\n", ptr != 0);

    return 0;
}
