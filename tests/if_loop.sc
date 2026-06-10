int main() {
    int score;
    int n;

    score = 85;
    if (score >= 90) {
        printf("Grade A\n");
    } else if (score >= 80) {
        printf("Grade B\n");
    } else {
        printf("Grade C\n");
    }

    n = 1;
    while (n <= 5) {
        printf("%d ", n);
        n++;
    }
    printf("\n");

    for (n = 1; n <= 5; n++) {
        if (n == 3) continue;
        printf("%d ", n);
    }
    printf("\n");

    return 0;
}
