using System;
using System.Collections.Generic;

namespace Helloworld
{
    class Program
    {
        static void Main(string[] args)
        {
            JustforTest();
            var fib = new List<int> {1, 1};
            for (int num = 0; num < 10; num++)
            {
                var pre1 = fib[fib.Count - 1];
                var pre2 = fib[fib.Count - 2];
                fib.Add(pre1 + pre2);
            }
            foreach (var item in fib)
                Console.WriteLine(item);
            
            // classes and objects
            var account = new BankAccount("VVangYZ", 1000);
            Console.WriteLine($"Account {account.Number} was created for {account.Owner} with {account.Balance} initial balance.");
            account.MakeDeposit(100, DateTime.Now, "Zyx give me my pin money!");
            Console.WriteLine(account.Balance);
            account.MakeWithdrawal(500, DateTime.Now, "Rent payment");
            Console.WriteLine(account.Balance);
            try
            {
                var invalidAccount = new BankAccount("invalid", -55);
            }
            catch (ArgumentOutOfRangeException e)
            {
                Console.WriteLine("Exception caught creating account with negative balance");
                Console.WriteLine(e.ToString());
            }
            Console.WriteLine(account.GetAcountHistory());
        }

        static void JustforTest()
        {   
            // 调用其他模块，打印简单字符串
            myClass cc = new myClass();
            Console.WriteLine($"Hello World! {cc.ReturnMessage()}");

            // 整型简单使用
            int a = 18;
            int b = 10;
            int c = a / b;
            Console.WriteLine(c);
            int max = int.MaxValue;
            int min = int.MinValue;
            Console.WriteLine($"The range of integers is {min} to {max}");

            // 双精度类型
            double a1 = 3;
            double b1 = 4;
            double c1 = a1/b1;
            Console.WriteLine(c1);
            double max1 = double.MaxValue;
            double min1 = double.MinValue;
            Console.WriteLine($"The range of double is {min1} to {max1}");

            // 奇怪的类型
            double c2 = 1.0/3.0;
            Console.WriteLine(c2);
            decimal a2 = 1.0M;
            decimal b2 = 3.0M;
            Console.WriteLine(a2/b2);
            double r = 2.5;
            double u = r * r * Math.PI;
            Console.WriteLine(u);

            // 判断语句
            int a3 = 5;
            int b3 = 6;
            if ((a3 + b3 > 10) && (a3 == b3))
            {
                Console.WriteLine("The answer is greater than ten.");
                Console.WriteLine("And the first number is equal to the second.");
            }
            else
            {
                Console.WriteLine("The answer is not greater than ten.");
                Console.WriteLine("Or the first number is not equal to the second.");
            }

            // 循环语句
            int counter = 0;
            while (counter < 10)
            {
                Console.WriteLine($"Hello world. The counter is {counter}.");
                counter++;
            }
            for(int aa = 0; aa < 10; aa++)
            {
                Console.WriteLine($"hi, wd. counter now is {aa}.");
            }

            // 列表
            var names = new List<string> {"<name>", "Ana", "Felipe"};
            names.Add("Wangxs");
            names.Add("LiuHH");
            names.Remove("<name>");
            names.Sort();
            foreach (var name in names)
            {
                Console.WriteLine($"Hello, {name.ToUpper()}!");
                Console.WriteLine($"The index of {name} is {names.IndexOf(name)}.");
            }
        }
    }
}
