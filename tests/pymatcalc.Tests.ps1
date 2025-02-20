BeforeAll {
    $com = "$PSScriptRoot/../src/pymatcalc.py"
    if ( $IsWindows ){
        $py = "python"
    } else {
        $py = "python3"
    }
}

Describe "pymatcalc" {
    Context "when value from pipeline received" {
        It "calculate matrix: A*B" {
            [string[]] $stdin  = @(
                "A 1 1",
                "A 2 4",
                "B 4 3",
                "B 2 1"
            )
            [string[]] $stdout = @(
                "A 1 1",
                "A 2 4",
                "B 4 3",
                "B 2 1",
                "A*B 4.0 3.0",
                "A*B 4.0 4.0"
            )
            $stdin | & $py $com 'A*B' | Should -Be $stdout
        }
        It "calculate matrix: A@B" {
            [string[]] $stdin  = @(
                "A 1 1",
                "A 2 4",
                "B 4 3",
                "B 2 1"
            )
            [string[]] $stdout = @(
                "A 1 1",
                "A 2 4",
                "B 4 3",
                "B 2 1",
                "A@B 6.0 4.0",
                "A@B 16.0 10.0"
            )
            $stdin | & $py $com 'A@B' | Should -Be $stdout
        }
        It "calculate matrix: np.matmul(A, B)" {
            [string[]] $stdin  = @(
                "A 1 1",
                "A 2 4",
                "B 4 3",
                "B 2 1"
            )
            [string[]] $stdout = @(
                "A 1 1",
                "A 2 4",
                "B 4 3",
                "B 2 1",
                "np.matmul(A,B) 6.0 4.0",
                "np.matmul(A,B) 16.0 10.0"
            )
            $stdin | & $py $com 'np.matmul(A, B)' | Should -Be $stdout
        }
        It "calculate matrix: C=np.eye(3,dtype=int)" {
            [string[]] $stdin  = @(
                "A 1 1",
                "A 2 4",
                "B 4 3",
                "B 2 1"
            )
            [string[]] $stdout = @(
                "A 1 1",
                "A 2 4",
                "B 4 3",
                "B 2 1",
                "C 1 0 0",
                "C 0 1 0",
                "C 0 0 1"
            )
            $stdin | & $py $com 'C=np.eye(3,dtype=int)' | Should -Be $stdout
        }
        It "calculate matrix: C=np.identity(3,dtype=int)" {
            [string[]] $stdin  = @(
                "A 1 1",
                "A 2 4",
                "B 4 3",
                "B 2 1"
            )
            [string[]] $stdout = @(
                "A 1 1",
                "A 2 4",
                "B 4 3",
                "B 2 1",
                "C 1 0 0",
                "C 0 1 0",
                "C 0 0 1"
            )
            $stdin | & $py $com 'C=np.identity(3,dtype=int)' | Should -Be $stdout
        }
        It "calculate matrix: add new label to ans" {
            [string[]] $stdin  = @(
                "A 1 1",
                "A 2 4",
                "B 4 3",
                "B 2 1"
            )
            [string[]] $stdout = @(
                "A 1 1",
                "A 2 4",
                "B 4 3",
                "B 2 1",
                "C 4.0 3.0",
                "C 4.0 4.0"
            )
            $stdin | & $py $com 'C=A*B' | Should -Be $stdout
        }
        It "calculate matrix: C=np.linalg.det(A)*np.eye(1)" {
            [string[]] $stdin  = @(
                "A 2 -6 4",
                "A 7 2 3",
                "A 8 5 -1"
            )
            [string[]] $stdout = @(
                "A 2 -6 4",
                "A 7 2 3",
                "A 8 5 -1",
                "C -144.0"
            )
            $stdin | & $py $com 'C=np.linalg.det(A)*np.eye(1)' | Should -Be $stdout
        }
        It "calculate matrix: invert" {
            [string[]] $stdin  = @(
                "A -4 2",
                "A 7 2"
            )
            [string[]] $stdout = @(
                "A -4 2",
                "A 7 2",
                "C -0.0909090909090909 0.09090909090909091",
                "C 0.3181818181818182 0.1818181818181818"
            )
            $stdin | & $py $com 'C=np.linalg.inv(A)' | Should -Be $stdout
        }
        It "calculate matrix: test invert" {
            [string[]] $stdin  = @(
                "A -4 2",
                "A 7 2"
            )
            [string[]] $stdout = @(
                "A -4 2",
                "A 7 2",
                "C 1.0 -5.551115123125783e-17",
                "C 1.1102230246251565e-16 1.0"
            )
            $stdin | & $py $com 'C=np.dot(A, np.linalg.inv(A))' | Should -Be $stdout
        }
        It "calculate matrix: chain calc using pipe1" {
            [string[]] $stdin  = @(
                "A 1 2",
                "A 3 4",
                "B 4 3",
                "B 2 1"
            )
            [string[]] $stdout = @(
                "A 1 2",
                "A 3 4",
                "B 4 3",
                "B 2 1",
                "C 8.0 5.0",
                "C 20.0 13.0",
                "D 48.0 31.0",
                "D 104.0 67.0"
            )
            $stdin | & $py $com 'C=A@B' | & $py $com 'D=A@C' | Should -Be $stdout
        }
        It "calculate matrix: chain calc using pipe2" {
            [string[]] $stdin  = @(
                "A 1 2",
                "A 3 4",
                "B 4 3",
                "B 2 1"
            )
            [string[]] $stdout = @(
                "A 1 2",
                "A 3 4",
                "B 4 3",
                "B 2 1",
                "C 48.0 31.0",
                "C 104.0 67.0"
            )
            $stdin | & $py $com 'C=A@(A@B)' | Should -Be $stdout
        }
    }
}

