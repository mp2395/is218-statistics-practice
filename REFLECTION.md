# Practice Calculator Reflection

## Successful adjustment request

For `adjust 3 offset=2 scale=4`, the parser splits the input into the operation name, the value `"3"`, and the named settings `"2"` and `"4"`. These start as strings. The factory selects `Operations.adjust`, checks that there is exactly one operand, and checks that the option names are allowed. It converts the supplied options to floats. The Calculation object converts the operand to a float and stores the operation and settings without executing them.

The parser returns a CalculateCommand. When the command executes, it asks the session to calculate the result. The operation adds the offset before multiplying by the scale, so `(3.0 + 2.0) * 4.0` produces `20.0`. The session saves the calculation and its actual result after execution succeeds. The command returns `Result: 20.0000`, which the CLI prints.

## Failed span request and last result

For `span 1`, the factory creates a calculation successfully because span does not have a fixed operand count in the factory. When the command asks the session to execute it, Operations.span checks the number of readings and raises ValueError because there is only one.

The exception passes through the calculation, session, and command to the CLI, which prints an error and allows another request. The session does not add an entry because execution failed before the history-saving step.

A following `last` request displays the previous successful calculation and its saved result. It does not execute the calculation again. If there was no previous successful calculation, it returns `History is empty.`

## Operations, commands, and the factory

Operations are static methods because they perform math using their inputs without needing an instance or session state. Commands are objects that represent application actions. For example, LastCommand uses its session to retrieve saved history.

`*values` collects positional arguments into a tuple. This lets span accept different numbers of readings. `**options` collects named arguments into a dictionary, such as offset and scale.

The factory selects an operation, checks its input policies, and constructs a Calculation. The command carries out an application action. Constructing a calculation and executing it are separate steps.

## Error handling

The span input check is an LBYL choice because it checks whether enough readings exist before calling max and min. This gives a clear error for both zero and one reading.

The CLI catches expected errors so an invalid request does not stop the program. Saving history only after successful execution prevents failed requests from changing the saved results.

## Tests

The adjustment tests check defaults, addition before multiplication, negative settings, and zero scale. The span tests check negative readings, duplicates, identical readings, and insufficient inputs.

The factory tests check numeric conversion, extra adjustment operands, unsupported span options, and deferred execution. The history tests check that failures leave saved entries unchanged and that clearing a returned list does not clear the session.

A tracked operation counts its executions. That test checks that the session executes once and LastCommand displays the saved result without executing again.

## Sources and assistance

I used the supplied is218-statistics-practice starter, including its calculation, history, parser, and testing infrastructure. 