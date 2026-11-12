import java.io.IOException;
import java.nio.file.Path;
import se.kth.prompt.GeneratePrompt;

class M4Check {
    public static void main(String[] args) throws Exception {
        Path dir = Path.of(args[0]);
        Path prompt = dir.resolve("prompt.txt");
        GeneratePrompt runner = new GeneratePrompt();

        String reply = runner.callPythonScript(dir.resolve("ok.py").toString(), prompt);
        if (!reply.strip().equals("mock reply")) {
            throw new AssertionError("Unexpected reply: " + reply);
        }
        System.out.println("PASS: successful call returned its reply");

        try {
            runner.callPythonScript(dir.resolve("fail.py").toString(), prompt);
            throw new AssertionError("Failed call was accepted");
        } catch (IOException e) {
            if (!e.getMessage().contains("exit code 1")
                    || !e.getMessage().contains("simulated model failure")) {
                throw new AssertionError("Failure details were lost", e);
            }
            System.out.println("PASS: failed call rejected; exit code and stderr preserved");
        }
    }
}
