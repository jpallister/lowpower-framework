
void exit(int a)
{
	while(1);
}

static unsigned int next = 1;

int rand_r()
{
    next = next * 1103515245 + 12345;
    return next;
}
