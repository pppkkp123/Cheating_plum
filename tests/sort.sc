void swap(int a, int b) {
    int tmp;
    tmp = a;
    a = b;
    b = tmp;
}

int main() {
    int data[8];
    int i;
    int j;
    int tmp;

    data[0] = 25;
    data[1] = 12;
    data[2] = 64;
    data[3] = 22;
    data[4] = 11;
    data[5] = 90;
    data[6] = 45;
    data[7] = 33;

    printf("Before sorting:\n");
    for (i = 0; i < 8; i++) {
        printf("%d ", data[i]);
    }
    printf("\n");

    for (i = 0; i < 8 - 1; i++) {
        for (j = 0; j < 8 - i - 1; j++) {
            if (data[j] > data[j + 1]) {
                tmp = data[j];
                data[j] = data[j + 1];
                data[j + 1] = tmp;
            }
        }
    }

    printf("After sorting:\n");
    for (i = 0; i < 8; i++) {
        printf("%d ", data[i]);
    }
    printf("\n");

    return 0;
}
