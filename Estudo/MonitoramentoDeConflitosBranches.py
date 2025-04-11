import subprocess

def run_git_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip().split('\n')

def get_remote_branches(exclude='main'):
    branches = run_git_command(['git', 'branch', '-r'])
    return [b.strip().replace('origin/', '') for b in branches if exclude not in b and '->' not in b]

def get_ahead_files(base_branch, target_branch):
    # Pega só os arquivos de commits que estão *ahead* da base
    files = run_git_command([
        'git', 'log', f'origin/{base_branch}..origin/{target_branch}',
        '--name-only', '--pretty=format:'
    ])
    return sorted(set([f for f in files if f.strip() != '']))

def main():
    print("🔄 Atualizando branches remotas...")
    subprocess.run(['git', 'fetch', 'origin'])

    base_branch = 'main'
    print(f"\n📂 Mostrando arquivos *ahead* da branch '{base_branch}':\n")

    branches = get_remote_branches(exclude=base_branch)
    ocupados = {}

    for branch in branches:
        print(f"🔍 Branch: {branch}")
        print("-" * 40)
        ahead_files = get_ahead_files(base_branch, branch)
        if ahead_files:
            for file in ahead_files:
                print(f"📄 {file}")
                ocupados.setdefault(file, []).append(branch)
        else:
            print("✅ Nenhuma modificação nova (ahead) em relação à main.")
        print()

    print("🧠 Arquivos modificados em múltiplas branches (ahead):")
    print("-" * 40)
    for file, branch_list in ocupados.items():
        if len(branch_list) > 1:
            print(f"{file} -> {', '.join(branch_list)}")

if __name__ == "__main__":
    main()
