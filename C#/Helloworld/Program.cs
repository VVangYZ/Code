using System;

namespace Helloworld
{
    class Program
    {
        static void WorkingWithIntegers()
        {
            myClass c1 = new myClass();
            Console.WriteLine($"Hello World! {c1.ReturnMessage()}");
            int a = 18;
            int b = 10;
            int c = a + b;
            Console.WriteLine(c);
            c = a / b;
            Console.WriteLine(c);
        }

        static void Main(string[] args)
        {
            WorkingWithIntegers();
        }
    }
}
