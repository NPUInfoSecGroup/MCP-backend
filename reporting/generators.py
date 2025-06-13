"""
Professional Markdown Report Generator for GHOSTCREW
Processes workflow conversation history and generates beautiful reports
"""

import json
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Any
import re
from colorama import Fore, Style


class PentestReportGenerator:
    """Generate professional penetration testing reports from workflow data"""
    
    def __init__(self, report_data: Dict[str, Any]):
        self.workflow_name = report_data['workflow_name']
        self.workflow_key = report_data['workflow_key']
        self.target = report_data['target']
        self.timestamp = report_data['timestamp']
        self.conversation_history = report_data['conversation_history']
        self.tools_used = report_data.get('tools_used', [])
        
        # Will be populated by AI analysis
        self.structured_findings = {}
        
    def format_conversation_history(self) -> str:
        """Format conversation history for AI analysis"""
        formatted = []
        
        for i, entry in enumerate(self.conversation_history, 1):
            formatted.append(f"\n--- STEP {i} ---")
            formatted.append(f"QUERY: {entry.get('user_query', '')}")
            formatted.append(f"RESPONSE: {entry.get('ai_response', '')}")
            formatted.append("=" * 50)
        
        return "\n".join(formatted)
    
    def create_analysis_prompt(self) -> str:
        """Create comprehensive analysis prompt for AI"""
        
        prompt = f"""
You are analyzing a complete penetration testing workflow to create a professional security assessment report.

ASSESSMENT DETAILS:
- Workflow: {self.workflow_name}
- Target: {self.target}
- Date: {self.timestamp.strftime('%Y-%m-%d')}
- Tools Available: {', '.join(self.tools_used) if self.tools_used else 'Various security tools'}

COMPLETE WORKFLOW CONVERSATION LOG:
{self.format_conversation_history()}

Please analyze this entire workflow and extract structured information. When extracting evidence, include the actual commands used and their outputs. Respond with a JSON object containing:

{{
  "executive_summary": "2-3 paragraph executive summary focusing on business impact and key risks",
  "key_statistics": {{
    "total_vulnerabilities": 0,
    "critical_count": 0,
    "high_count": 0,
    "systems_tested": 0,
    "systems_compromised": 0
  }},
  "vulnerabilities": [
    {{
      "severity": "Critical|High|Medium|Low|Informational",
      "title": "Descriptive vulnerability title",
      "description": "Technical description of the vulnerability",
      "impact": "Business impact if exploited",
      "affected_systems": ["IP/hostname"],
      "remediation": "Specific remediation steps",
      "evidence": "Include actual commands used and key outputs that demonstrate this finding. Format as: 'Command: [command] Output: [relevant output]'",
      "cvss_score": "If applicable",
      "references": ["CVE numbers, links, etc."]
    }}
  ],
  "compromised_systems": [
    {{
      "system": "IP/hostname", 
      "access_level": "user|admin|root|system",
      "method": "How access was gained",
      "evidence": "Actual commands and outputs showing compromise"
    }}
  ],
  "credentials_found": [
    {{
      "username": "username",
      "credential_type": "password|hash|token|key",
      "system": "where found",
      "strength": "weak|moderate|strong"
    }}
  ],
  "tools_used": ["List of tools actually used in testing"],
  "attack_paths": [
    {{
      "path_description": "Description of attack chain",
      "steps": ["Step 1", "Step 2", "etc"],
      "impact": "What this path achieves"
    }}
  ],
  "recommendations": [
    {{
      "priority": "Immediate|Short-term|Medium-term|Long-term",
      "category": "Network|Application|System|Process",
      "recommendation": "Specific actionable recommendation",
      "business_justification": "Why this is important for business"
    }}
  ],
  "methodology": "Brief description of testing methodology used",
  "scope_limitations": "Any scope limitations or areas not tested",
  "conclusion": "Overall security posture assessment and key takeaways"
}}

Focus on extracting real findings from the conversation. Include actual command examples and outputs in the evidence fields. If no vulnerabilities were found, that's also valuable information. Be accurate and professional.
"""
        return prompt
    
    async def analyze_with_ai(self, prompt: str, run_agent_func, connected_servers, kb_instance=None):
        """Run AI analysis using the main agent function"""
        try:
            # Use streaming=True since run_agent doesn't properly handle streaming=False
            result = await run_agent_func(
                prompt, 
                connected_servers, 
                history=[], 
                streaming=True, 
                kb_instance=kb_instance
            )
            
            if result and hasattr(result, "final_output"):
                return result.final_output
            return None
            
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return None
    
    def parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response and extract JSON data"""
        try:
            # Try to find JSON in the response
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = ai_response[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback - create basic structure
                return {
                    "executive_summary": ai_response[:500] + "...",
                    "key_statistics": {"total_vulnerabilities": 0},
                    "vulnerabilities": [],
                    "compromised_systems": [],
                    "recommendations": [],
                    "methodology": "Standard penetration testing methodology",
                    "conclusion": "Assessment completed successfully."
                }
                
        except json.JSONDecodeError:
            # Fallback structure
            return {
                "executive_summary": "Assessment completed. See technical findings for details.",
                "key_statistics": {"total_vulnerabilities": 0},
                "vulnerabilities": [],
                "compromised_systems": [],
                "recommendations": [],
                "methodology": "Standard penetration testing methodology", 
                "conclusion": "Unable to parse detailed findings."
            }
    
    def generate_markdown_report(self) -> str:
        """Generate the final markdown report"""
        findings = self.structured_findings
        
        report = []
        
        # Title Page
        report.append(f"# Penetration Testing Report")
        report.append(f"\n## {self.workflow_name}")
        report.append(f"\n**Target:** {self.target}  ")
        report.append(f"**Assessment Date:** {self.timestamp.strftime('%Y-%m-%d')}  ")
        report.append(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
        report.append(f"**Report ID:** GHOSTCREW-{self.workflow_key}-{int(self.timestamp.timestamp())}  ")
        report.append(f"\n---\n")
        
        # Table of Contents
        report.append("## Table of Contents\n")
        report.append("1. [Executive Summary](#1-executive-summary)")
        report.append("2. [Assessment Overview](#2-assessment-overview)")
        report.append("3. [Key Findings](#3-key-findings)")
        report.append("4. [Vulnerability Details](#4-vulnerability-details)")
        report.append("5. [Compromised Systems](#5-compromised-systems)")
        report.append("6. [Attack Paths](#6-attack-paths)")
        report.append("7. [Recommendations](#7-recommendations)")
        report.append("8. [Technical Methodology](#8-technical-methodology)")
        report.append("9. [Conclusion](#9-conclusion)")
        report.append("\n---\n")
        
        # Executive Summary
        report.append("## 1. Executive Summary\n")
        report.append(findings.get('executive_summary', 'Assessment completed successfully.'))
        report.append("\n---\n")
        
        # Assessment Overview
        report.append("## 2. Assessment Overview\n")
        report.append(f"### Scope")
        report.append(f"- **Primary Target:** {self.target}")
        report.append(f"- **Assessment Type:** {self.workflow_name}")
        report.append(f"- **Testing Window:** {self.timestamp.strftime('%Y-%m-%d')}")
        
        if self.tools_used:
            report.append(f"\n### Tools Used")
            for tool in self.tools_used:
                report.append(f"- {tool}")
        
        stats = findings.get('key_statistics', {})
        if stats:
            report.append(f"\n### Key Statistics")
            report.append(f"- **Total Vulnerabilities:** {stats.get('total_vulnerabilities', 0)}")
            report.append(f"- **Critical Severity:** {stats.get('critical_count', 0)}")
            report.append(f"- **High Severity:** {stats.get('high_count', 0)}")
            report.append(f"- **Systems Compromised:** {stats.get('systems_compromised', 0)}")
        
        report.append("\n---\n")
        
        # Key Findings Summary
        report.append("## 3. Key Findings\n")
        
        vulnerabilities = findings.get('vulnerabilities', [])
        if vulnerabilities:
            # Group by severity
            severity_groups = {'Critical': [], 'High': [], 'Medium': [], 'Low': [], 'Informational': []}
            for vuln in vulnerabilities:
                severity = vuln.get('severity', 'Low')
                if severity in severity_groups:
                    severity_groups[severity].append(vuln)
            
            report.append("### Vulnerability Summary\n")
            report.append("| Severity | Count | Description |")
            report.append("|----------|-------|-------------|")
            
            for severity, vulns in severity_groups.items():
                if vulns:
                    count = len(vulns)
                    titles = [v.get('title', 'Unknown') for v in vulns[:3]]
                    desc = ', '.join(titles)
                    if len(vulns) > 3:
                        desc += f' (and {len(vulns) - 3} more)'
                    report.append(f"| {severity} | {count} | {desc} |")
        else:
            report.append("No significant vulnerabilities were identified during the assessment.")
        
        report.append("\n---\n")
        
        # Vulnerability Details
        report.append("## 4. Vulnerability Details\n")
        
        if vulnerabilities:
            # Group by severity for detailed listing
            for severity in ['Critical', 'High', 'Medium', 'Low', 'Informational']:
                severity_vulns = [v for v in vulnerabilities if v.get('severity') == severity]
                
                if severity_vulns:
                    report.append(f"### {severity} Severity Vulnerabilities\n")
                    
                    for i, vuln in enumerate(severity_vulns, 1):
                        report.append(f"#### {severity.upper()}-{i:03d}: {vuln.get('title', 'Unknown Vulnerability')}\n")
                        report.append(f"**Description:** {vuln.get('description', 'No description provided')}\n")
                        report.append(f"**Impact:** {vuln.get('impact', 'Impact assessment pending')}\n")
                        
                        if vuln.get('affected_systems'):
                            report.append(f"**Affected Systems:** {', '.join(vuln['affected_systems'])}\n")
                        
                        report.append(f"**Remediation:** {vuln.get('remediation', 'Remediation steps pending')}\n")
                        
                        if vuln.get('evidence'):
                            report.append(f"**Evidence:**")
                            report.append("```")
                            report.append(vuln['evidence'])
                            report.append("```")
                        
                        if vuln.get('references'):
                            report.append(f"**References:** {', '.join(vuln['references'])}\n")
                        
                        report.append("\n")
        else:
            report.append("No vulnerabilities were identified during this assessment.")
        
        report.append("---\n")
        
        # Compromised Systems
        report.append("## 5. Compromised Systems\n")
        
        compromised = findings.get('compromised_systems', [])
        if compromised:
            report.append("| System | Access Level | Method | Evidence |")
            report.append("|--------|--------------|--------|----------|")
            
            for system in compromised:
                report.append(f"| {system.get('system', 'Unknown')} | {system.get('access_level', 'Unknown')} | {system.get('method', 'Unknown')} | {system.get('evidence', 'See technical details')[:50]}{'...' if len(system.get('evidence', '')) > 50 else ''} |")
        else:
            report.append("No systems were successfully compromised during the assessment.")
        
        report.append("\n---\n")
        
        # Attack Paths
        report.append("## 6. Attack Paths\n")
        
        attack_paths = findings.get('attack_paths', [])
        if attack_paths:
            for i, path in enumerate(attack_paths, 1):
                report.append(f"### Attack Path {i}: {path.get('path_description', 'Unknown Path')}\n")
                report.append(f"**Impact:** {path.get('impact', 'Unknown impact')}\n")
                
                steps = path.get('steps', [])
                if steps:
                    report.append("**Steps:**")
                    for step_num, step in enumerate(steps, 1):
                        report.append(f"{step_num}. {step}")
                report.append("\n")
        else:
            report.append("No specific attack paths were identified or documented.")
        
        report.append("---\n")
        
        # Recommendations
        report.append("## 7. Recommendations\n")
        
        recommendations = findings.get('recommendations', [])
        if recommendations:
            # Group by priority
            priority_groups = {'Immediate': [], 'Short-term': [], 'Medium-term': [], 'Long-term': []}
            for rec in recommendations:
                priority = rec.get('priority', 'Medium-term')
                if priority in priority_groups:
                    priority_groups[priority].append(rec)
            
            for priority, recs in priority_groups.items():
                if recs:
                    report.append(f"### {priority} Priority\n")
                    for rec in recs:
                        report.append(f"**{rec.get('category', 'General')}:** {rec.get('recommendation', 'No recommendation provided')}")
                        if rec.get('business_justification'):
                            report.append(f"  \n*Business Justification:* {rec['business_justification']}")
                        report.append("\n")
        else:
            report.append("Continue following security best practices and conduct regular assessments.")
        
        report.append("---\n")
        
        # Technical Methodology
        report.append("## 8. Technical Methodology\n")
        report.append(findings.get('methodology', 'Standard penetration testing methodology was followed.'))
        
        if findings.get('scope_limitations'):
            report.append(f"\n### Scope Limitations\n")
            report.append(findings['scope_limitations'])
        
        report.append("\n---\n")
        
        # Conclusion
        report.append("## 9. Conclusion\n")
        report.append(findings.get('conclusion', 'Assessment completed successfully.'))
        
        report.append(f"\n\n---\n")
        report.append(f"*Report generated by GHOSTCREW v0.1.0*  ")
        report.append(f"*{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return "\n".join(report)
    
    async def generate_report(self, run_agent_func, connected_servers, kb_instance=None, save_raw_history=False) -> str:
        """Main method to generate the complete report"""
        
        print(f"Analyzing workflow findings...")
        
        # Step 1: Create analysis prompt
        analysis_prompt = self.create_analysis_prompt()
        
        # Step 2: Get AI analysis
        ai_response = await self.analyze_with_ai(
            analysis_prompt, 
            run_agent_func, 
            connected_servers, 
            kb_instance
        )
        
        if not ai_response:
            raise Exception("Failed to get AI analysis")
        
        print(f"Extracting structured findings...")
        
        # Step 3: Parse AI response
        self.structured_findings = self.parse_ai_response(ai_response)
        
        print(f"Generating markdown report...")
        
        # Step 4: Generate markdown report
        markdown_report = self.generate_markdown_report()
        
        # Step 5: Save report with options
        report_filename = self.save_report(markdown_report, save_raw_history)
        
        return report_filename
    
    def save_report(self, markdown_content: str, save_raw_history: bool = False) -> str:
        """Save the report to file with optional raw history"""
        
        # Create reports directory if it doesn't exist
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        # Generate filename
        timestamp_str = str(int(self.timestamp.timestamp()))
        filename = f"{reports_dir}/ghostcrew_{self.workflow_key}_{timestamp_str}.md"
        
        # Save markdown file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Optionally save raw conversation history
        if save_raw_history:
            raw_history_content = []
            raw_history_content.append(f"GHOSTCREW Raw Workflow History")
            raw_history_content.append(f"Workflow: {self.workflow_name}")
            raw_history_content.append(f"Target: {self.target}")
            raw_history_content.append(f"Date: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            raw_history_content.append(f"=" * 60)
            raw_history_content.append("")
            
            for i, entry in enumerate(self.conversation_history, 1):
                raw_history_content.append(f"STEP {i} - QUERY:")
                raw_history_content.append("-" * 40)
                raw_history_content.append(entry.get('user_query', 'No query recorded'))
                raw_history_content.append("")
                raw_history_content.append(f"STEP {i} - AI RESPONSE:")
                raw_history_content.append("-" * 40)
                raw_history_content.append(entry.get('ai_response', 'No response recorded'))
                raw_history_content.append("")
                raw_history_content.append("=" * 60)
                raw_history_content.append("")
            
            raw_filename = f"{reports_dir}/ghostcrew_{self.workflow_key}_{timestamp_str}_raw_history.txt"
            with open(raw_filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(raw_history_content))
            print(f"Raw conversation history saved: {raw_filename}")
        
        return filename


async def generate_report_from_workflow(report_data: Dict[str, Any], run_agent_func, connected_servers, kb_instance=None, save_raw_history=False) -> str:
    """
    Main function to generate a professional report from workflow data
    
    Args:
        report_data: Dictionary containing workflow information
        run_agent_func: The main agent function for AI analysis
        connected_servers: Connected MCP servers
        kb_instance: Knowledge base instance
        save_raw_history: Whether to save raw conversation history
        
    Returns:
        str: Path to generated report file
    """
    
    generator = PentestReportGenerator(report_data)
    return await generator.generate_report(run_agent_func, connected_servers, kb_instance, save_raw_history)


async def generate_report_from_ptt(ptt_manager, conversation_history: List[Dict[str, Any]], run_agent_func=None, connected_servers=None, kb_instance=None, save_raw_history=False) -> str:
    """
    Generate a professional report from PTT (Pentesting Task Tree) data
    
    Args:
        ptt_manager: TaskTreeManager instance containing the PTT
        conversation_history: List of conversation history entries
        run_agent_func: The main agent function for AI analysis
        connected_servers: Connected MCP servers
        kb_instance: Knowledge base instance
        save_raw_history: Whether to save raw conversation history
        
    Returns:
        str: Path to generated report file
    """
    
    # Convert PTT data to report-compatible format
    report_data = {
        'workflow_name': f"Agent Mode: {ptt_manager.goal}",
        'workflow_key': 'agent_mode',
        'target': ptt_manager.target,
        'timestamp': ptt_manager.creation_time,
        'conversation_history': conversation_history,
        'tools_used': [server.name for server in connected_servers] if connected_servers else [],
        'ptt_data': {
            'goal': ptt_manager.goal,
            'target': ptt_manager.target,
            'constraints': ptt_manager.constraints,
            'statistics': ptt_manager.get_statistics(),
            'tree_structure': ptt_manager.to_natural_language(),
            'nodes': {node_id: node.to_dict() for node_id, node in ptt_manager.nodes.items()}
        }
    }
    
    # Create a specialized PTT report generator
    generator = PTTReportGenerator(report_data)
    
    if run_agent_func and connected_servers:
        return await generator.generate_report(run_agent_func, connected_servers, kb_instance, save_raw_history)
    else:
        # Generate a basic report without AI analysis if no agent function available
        return generator.generate_basic_report(save_raw_history)


class PTTReportGenerator:
    """Generate professional penetration testing reports from PTT data"""
    
    def __init__(self, report_data: Dict[str, Any]):
        self.workflow_name = report_data['workflow_name']
        self.workflow_key = report_data['workflow_key']
        self.target = report_data['target']
        self.timestamp = report_data['timestamp']
        self.conversation_history = report_data['conversation_history']
        self.tools_used = report_data.get('tools_used', [])
        self.ptt_data = report_data.get('ptt_data', {})
        
        # Will be populated by AI analysis
        self.structured_findings = {}
    
    def generate_basic_report(self, save_raw_history: bool = False) -> str:
        """Generate a basic report without AI analysis"""
        # Extract findings from PTT nodes
        vulnerabilities = []
        completed_tasks = []
        failed_tasks = []
        
        for node_data in self.ptt_data.get('nodes', {}).values():
            if node_data.get('status') == 'completed' and node_data.get('findings'):
                completed_tasks.append({
                    'description': node_data.get('description', ''),
                    'findings': node_data.get('findings', ''),
                    'tool_used': node_data.get('tool_used', ''),
                    'output_summary': node_data.get('output_summary', '')
                })
            elif node_data.get('status') == 'vulnerable':
                vulnerabilities.append({
                    'title': node_data.get('description', 'Unknown Vulnerability'),
                    'description': node_data.get('findings', 'No description available'),
                    'severity': 'Medium',  # Default severity
                    'affected_systems': [self.target],
                    'evidence': node_data.get('output_summary', ''),
                    'remediation': 'Review and patch identified vulnerabilities'
                })
            elif node_data.get('status') == 'failed':
                failed_tasks.append({
                    'description': node_data.get('description', ''),
                    'tool_used': node_data.get('tool_used', ''),
                    'error': node_data.get('output_summary', '')
                })
        
        # Create structured findings
        self.structured_findings = {
            'executive_summary': f"Autonomous penetration testing completed against {self.target}. Goal: {self.ptt_data.get('goal', 'Unknown')}. {len(completed_tasks)} tasks completed successfully, {len(vulnerabilities)} vulnerabilities identified.",
            'vulnerabilities': vulnerabilities,
            'key_statistics': {
                'total_vulnerabilities': len(vulnerabilities),
                'critical_count': 0,
                'high_count': 0,
                'medium_count': len(vulnerabilities),
                'systems_compromised': 1 if vulnerabilities else 0
            },
            'methodology': f"Autonomous penetration testing using Pentesting Task Tree (PTT) methodology with intelligent task prioritization and execution.",
            'conclusion': f"Assessment {'successfully identified security weaknesses' if vulnerabilities else 'completed without identifying critical vulnerabilities'}. {'Immediate remediation recommended' if vulnerabilities else 'Continue monitoring and regular assessments'}.",
            'recommendations': [
                {
                    'category': 'Patch Management',
                    'recommendation': 'Apply security patches to all identified vulnerable services',
                    'priority': 'Immediate',
                    'business_justification': 'Prevents exploitation of known vulnerabilities'
                },
                {
                    'category': 'Monitoring',
                    'recommendation': 'Implement monitoring for the services and ports identified during reconnaissance',
                    'priority': 'Short-term',
                    'business_justification': 'Early detection of potential security incidents'
                }
            ] if vulnerabilities else [
                {
                    'category': 'Continued Security',
                    'recommendation': 'Maintain current security posture and conduct regular assessments',
                    'priority': 'Medium-term',
                    'business_justification': 'Proactive security maintenance'
                }
            ]
        }
        
        # Generate the markdown report
        markdown_report = self.generate_markdown_report()
        
        # Save report
        return self.save_report(markdown_report, save_raw_history)
    
    async def generate_report(self, run_agent_func, connected_servers, kb_instance=None, save_raw_history=False) -> str:
        """Generate a comprehensive report with AI analysis"""
        try:
            # Create analysis prompt specifically for PTT data
            analysis_prompt = self.create_ptt_analysis_prompt()
            
            # Get AI analysis
            ai_response = await self.analyze_with_ai(
                analysis_prompt,
                run_agent_func,
                connected_servers,
                kb_instance
            )
            
            if ai_response:
                # Parse AI response
                self.structured_findings = self.parse_ai_response(ai_response)
            else:
                print(f"{Fore.YELLOW}AI analysis failed, generating basic report...{Style.RESET_ALL}")
                return self.generate_basic_report(save_raw_history)
            
        except Exception as e:
            print(f"{Fore.YELLOW}Error in AI analysis: {e}. Generating basic report...{Style.RESET_ALL}")
            return self.generate_basic_report(save_raw_history)
        
        # Generate markdown report
        markdown_report = self.generate_markdown_report()
        
        # Save report
        return self.save_report(markdown_report, save_raw_history)
    
    def create_ptt_analysis_prompt(self) -> str:
        """Create analysis prompt for PTT data"""
        ptt_structure = self.ptt_data.get('tree_structure', 'No PTT structure available')
        goal = self.ptt_data.get('goal', 'Unknown goal')
        target = self.target
        statistics = self.ptt_data.get('statistics', {})
        
        # Extract key findings from completed tasks
        key_findings = []
        for node_data in self.ptt_data.get('nodes', {}).values():
            if node_data.get('status') in ['completed', 'vulnerable'] and node_data.get('findings'):
                key_findings.append(f"- {node_data.get('description', '')}: {node_data.get('findings', '')}")
        
        findings_text = '\n'.join(key_findings) if key_findings else 'No significant findings recorded'
        
        prompt = f"""You are analyzing the results of an autonomous penetration test conducted using a Pentesting Task Tree (PTT) methodology.

ASSESSMENT DETAILS:
Goal: {goal}
Target: {target}
Statistics: {statistics}

PTT STRUCTURE:
{ptt_structure}

KEY FINDINGS:
{findings_text}

Based on this PTT analysis, provide a comprehensive security assessment in the following JSON format:

{{
    "executive_summary": "Professional executive summary of the assessment",
    "key_statistics": {{
        "total_vulnerabilities": 0,
        "critical_count": 0,
        "high_count": 0,
        "medium_count": 0,
        "low_count": 0,
        "systems_compromised": 0
    }},
    "vulnerabilities": [
        {{
            "title": "Vulnerability name",
            "description": "Detailed description",
            "severity": "Critical/High/Medium/Low",
            "impact": "Business impact description",
            "affected_systems": ["system1", "system2"],
            "evidence": "Technical evidence",
            "remediation": "Specific remediation steps",
            "references": ["CVE-XXXX", "reference links"]
        }}
    ],
    "compromised_systems": [
        {{
            "system": "system identifier",
            "access_level": "user/admin/root",
            "method": "exploitation method",
            "evidence": "proof of compromise"
        }}
    ],
    "attack_paths": [
        {{
            "path_description": "Attack path name",
            "impact": "potential impact",
            "steps": ["step1", "step2", "step3"]
        }}
    ],
    "recommendations": [
        {{
            "category": "category name",
            "recommendation": "specific recommendation",
            "priority": "Immediate/Short-term/Medium-term/Long-term",
            "business_justification": "why this matters to business"
        }}
    ],
    "methodology": "Description of the PTT methodology used",
    "conclusion": "Professional conclusion of the assessment"
}}

Focus on:
1. Extracting real security findings from the PTT execution
2. Proper risk classification
3. Actionable recommendations
4. Business-relevant impact assessment"""

        return prompt
    
    async def analyze_with_ai(self, prompt: str, run_agent_func, connected_servers, kb_instance) -> str:
        """Analyze the assessment with AI"""
        try:
            result = await run_agent_func(
                prompt,
                connected_servers,
                history=[],
                streaming=True,
                kb_instance=kb_instance
            )
            
            if hasattr(result, "final_output"):
                return result.final_output
            elif hasattr(result, "output"):
                return result.output
            elif isinstance(result, str):
                return result
            
        except Exception as e:
            print(f"{Fore.RED}Error in AI analysis: {e}{Style.RESET_ALL}")
        
        return None
    
    def parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response for structured findings"""
        try:
            # Try to extract JSON from the response
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            
        except Exception as e:
            print(f"{Fore.YELLOW}Failed to parse AI response: {e}{Style.RESET_ALL}")
        
        # Fallback to basic findings
        return {
            'executive_summary': 'Assessment completed successfully.',
            'vulnerabilities': [],
            'key_statistics': {'total_vulnerabilities': 0},
            'methodology': 'Autonomous penetration testing using PTT methodology.',
            'conclusion': 'Assessment completed.',
            'recommendations': []
        }
    
    def generate_markdown_report(self) -> str:
        """Generate the final markdown report using the same format as PentestReportGenerator"""
        # Use the same report generation logic as the workflow reporter
        temp_generator = PentestReportGenerator({
            'workflow_name': self.workflow_name,
            'workflow_key': self.workflow_key,
            'target': self.target,
            'timestamp': self.timestamp,
            'conversation_history': self.conversation_history,
            'tools_used': self.tools_used
        })
        temp_generator.structured_findings = self.structured_findings
        
        return temp_generator.generate_markdown_report()
    
    def save_report(self, markdown_content: str, save_raw_history: bool = False) -> str:
        """Save the report to file"""
        # Create reports directory if it doesn't exist
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        # Generate filename
        timestamp_str = str(int(self.timestamp.timestamp()))
        safe_target = re.sub(r'[^\w\-_\.]', '_', self.target)
        filename = f"{reports_dir}/ghostcrew_agent_mode_{safe_target}_{timestamp_str}.md"
        
        # Save markdown file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Optionally save raw history and PTT data
        if save_raw_history:
            raw_filename = f"{reports_dir}/ghostcrew_agent_mode_{safe_target}_{timestamp_str}_raw.json"
            raw_data = {
                'ptt_data': self.ptt_data,
                'conversation_history': self.conversation_history,
                'timestamp': self.timestamp.isoformat()
            }
            
            with open(raw_filename, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, indent=2, default=str)
            
            print(f"{Fore.GREEN}Raw PTT data saved: {raw_filename}{Style.RESET_ALL}")
        
        return filename 