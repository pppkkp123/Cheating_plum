int main() {
    int x;
    int *ptr;

    x = 10;
    ptr = &x;

    printf("x = %d\n", x);
    printf("*ptr = %d\n", *ptr);

    *ptr = 99;
    printf("after *ptr = 99, x = %d\n", x);

    x = 123;
    printf("after x = 123, *ptr = %d\n", *ptr);
    printf("ptr address = %d\n", ptr);

    return 0;
}
