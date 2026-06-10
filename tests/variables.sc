int x;

int main() {
    int y;
    int z;
    x = 10;
    y = 20;
    z = x + y;
    printf("x=%d, y=%d, z=%d\n", x, y, z);

    y += 5;
    z = y * 2;
    printf("y=%d, z=%d\n", y, z);

    return 0;
}
