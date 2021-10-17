// @Time    : 2021.10.17
// @Author  : Xueshan Zhang
// @File    : F:\Software\go\go\Project\src\GoBasics1.go

package main 										  // declare main packge

import "fmt"

func main() { 										  // declare main function, the entrance
	fmt.Println("tom\tjack")                      // 1. \t
	fmt.Println("tom\njack")                      // 2. \n
	fmt.Println("F:\\Software\\go\\go\\Project")  // 3. \\
	fmt.Println("tom says 'I love you.'")
	fmt.Println("tom says \"I love you too.\"")   // 4. \"
	fmt.Println("Love is patience. \r Life")      // 5. \r
	fmt.Println("Love is patience." +
		"Life")
	fmt.Println("Name\tAge\tHome\tWork\nJohn\t15\tA\tB") // 6. Composite
}


// Results:
/*
PS F:\Software\go\go\Project> go run .\src\helloworld.go
tom     jack
tom
jack
F:\Software\go\go\Project
tom says 'I love you'
tom says "I love you too."
 Lifeis patience.
Love is patience.Life
Name    Age     Home    Work
John    15      A       B
PS F:\Software\go\go\Project> clear
PS F:\Software\go\go\Project> go run .\src\GoBasics1.go
tom     jack
tom
jack
F:\Software\go\go\Project
tom says 'I love you.'
tom says "I love you too."
 Lifeis patience.
Love is patience.Life
Name    Age     Home    Work
John    15      A       B
 */