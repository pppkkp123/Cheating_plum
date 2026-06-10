int main() {
    int arr[3];
    int *p;

    arr[0] = 10;
    arr[1] = 20;
    arr[2] = 30;

    p = &arr[1];
    printf("before: arr[1] = %d\n", arr[1]);

    *p = 88;
    printf("after: arr[1] = %d\n", arr[1]);
    printf("*p = %d\n", *p);

    return 0;
}
