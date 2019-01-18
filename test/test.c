//
// Created by tefx on 12/26/18.
//

#include <stdio.h>
#include <malloc.h>
#include <string.h>
#include "test_gen.h"


int main(void) {
    test_amcp_connect("tcp://localhost:5555");
//    for (int i = 0; i < 100000; ++i) {
//        test_add(1, 2.4);
//    }
    printf("Ret: %f\n", test_add(1, 2.5));
    printf("Ret: %f\n", test_mul(2, 5.5));
    printf("Ret: %d\n", test_double(10));
    printf("Ret: %s\n", test_upper("abc"));

    double a = 1;
    printf("Ret: %f\n", test_inc(&a));
    printf("Ref: %f\n", a);

    char* s = malloc(sizeof(char) * 4);
    memcpy(s, "abc", 4);
    test_upper_inplace(s);
    printf("Ref: %s\n", s);
    free(s);

    test_amcp_close();
    return 0;
}