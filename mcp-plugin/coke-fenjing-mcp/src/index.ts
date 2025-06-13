#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { spawn } from 'child_process';

const fenjingPath = process.env.FENJING_PATH;
if (!fenjingPath) {
    console.error("FENJING_PATH environment variable not set");
    process.exit(1);
}

// const args = process.argv.slice(2);
// if (args.length === 0) {
//     console.error("Usage: fenjing-mcp fenjing [OPTIONS] COMMAND [ARGS]...");
//     process.exit(1);
// }

// Create server instance
const server = new McpServer({
    name: "fenjing",
    version: "1.0.0",
});

server.tool(
    "do-fenjing",
    "Run fenjing with specified URL in various modes",
    {
        mode: z.enum(["scan", "crack"]).describe(`Fenjing Usage

Modes:

crack           攻击指定的表单
scan            扫描指定的网站

Examples: 
fenjing scan --url http://example.com --inputs name,age --method GET

fenjing crack --url http://example.com --inputs name,age --method POST --exec-cmd whoami
            `),
        url: z.string().url().describe("Target URL to detect Server Side Template Injection (SSTI) vulnerabilities"),
        fenjing_args: z.array(z.string()).describe(`Additional fenjing arguments 
            
Options:
  --no-verify-ssl                 不验证SSL证书
  --proxy TEXT                    请求时使用的代理
  --extra-data TEXT               请求时的额外POST参数，如a=1&b=2
  --extra-params TEXT             请求时的额外GET参数，如a=1&b=2
  --cookies TEXT                  请求时使用的Cookie
  --header TEXT                   请求时使用的Headers
  --user-agent TEXT               请求时使用的User Agent
  --interval FLOAT                每次请求的间隔
  --tamper-cmd TEXT               在发送payload之前进行编码的命令，默认不进行额外操作
  --waf-keyword TEXT              手动指定waf页面含有的关键字，此时不会自动检测waf页面的哈希等。可指定多个关键字
  --find-flag FINDFLAG            是否自动寻找flag，默认只在WAF较好绕过时自动寻找flag
  --detect-waf-keywords DETECTWAFKEYWORDS
                                  是否枚举被waf的关键字，需要额外时间，默认为none, 可选full/fast
  --environment TEMPLATEENVIRONMENT
                                  模板的执行环境，默认为不带flask全局变量的普通jinja2
  --replaced-keyword-strategy REPLACEDKEYWORDSTRATEGY
                                  WAF替换关键字时的策略，可为avoid/ignore/doubletapping
  --detect-mode DETECTMODE        分析模式，可为accurate或fast
  -e, --exec-cmd TEXT             成功后执行的shell指令，不填则成功后进入交互模式
  -a, --action TEXT               参数的提交路径，如果和URL中的路径不同则需要填入
  -m, --method TEXT               参数的提交方式，默认为POST
  -i, --inputs TEXT               所有参数，以逗号分隔  [required]
  --eval-args-payload             是否开启在GET参数中传递Eval payload的功能
  --help                          Show this message and exit.

  an exploit example could be: fenjing crack --url ctf.npusec.org.cn:12074 --inputs name --method GET --exec-cmd whoami

  pls remember that if you want to use the crack mode, you must specify the url and inputs parameter, which is a comma-separated list of all parameters that you want to test for SSTI vulnerabilities. For example, if you want to test the "name" and "age" parameters, you can use --inputs name,age, and you must also specify the --exec-cmd parameter to execute a command after the attack is successful. For example, you can use --exec-cmd whoami to execute the whoami command after the attack is successful.
    `),
    },
    async ({ mode, url, fenjing_args }) => {
        const fenjing = spawn(fenjingPath, [mode ,'-u', url, ...fenjing_args]);
        let output = '';

        // Handle stdout
        fenjing.stdout.on('data', (data) => {
            output += data.toString();
        });

        // Handle stderr
        fenjing.stderr.on('data', (data) => {
            output += data.toString();
        });

        // Handle process completion
        return new Promise((resolve, reject) => {
            fenjing.on('close', (code) => {
                if (code === 0) {
                    resolve({
                        content: [{
                            type: "text",
                            text: output + "\n fenjing completed successfully"
                        }]
                    });
                } else {
                    reject(new Error(`fenjing exited with code ${code}`));
                }
            });

            fenjing.on('error', (error) => {
                reject(new Error(`Failed to start fenjing: ${error.message}`));
            });
        });
    },
);

// Start the server
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("fenjing MCP Server running on stdio");
}

main().catch((error) => {
    console.error("Fatal error in main():", error);
    process.exit(1);
});