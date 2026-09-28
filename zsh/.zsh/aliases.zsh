# Unix commands.
alias ll='ls -lhA'
alias cd..='cd ..'
alias clip='xclip -selection clipboard'
alias sn='screen'
alias tb='conda activate torch; tensorboard --logdir'
alias diskspace='df -h ${HOME}'
alias h='fc -l'
alias resource='source ${HOME}/.bashrc'
alias basha='vim ${HOME}/.bash_aliases'
alias myfind='find . -name '
alias hist='history'

alias pya='ps ax | grep "python3"'
alias pyk='kill $(ps ax | grep "python" | cut -d " " -f 1)'
alias py3k='kill $(ps ax | grep "python3" | cut -d " " -f 1)'
alias py='python3'
alias tba='ps ax | grep tensorboard'
alias tbk='kill $(ps ax | grep "tensorboard" | cut -d " " -f 1)'
alias hgrep='fc -l -1000 | grep '
alias remote='cd $HOME/remote'
alias gpu='nvidia-smi'


# Git specifics.
alias st='git status'
alias pull='git pull'
alias push='git push'
alias pushtags='git push origin --tags'
alias br='git branch'
alias add='git add'
alias cm='git commit'
alias scm='SKIP=flake8,isort,black git commit'
alias dif='git diff'
alias branch='git branch'
alias cdif='git diff --staged'
alias master='git checkout master'
alias jnote='jupyter-notebook'
alias jlab='jupyter-lab'
alias gcheck='git checkout'
alias rebase='git rebase'
alias gbc='git rebase --continue'

# Git commands without ssh key but with Github Token.
alias gpull='git -c credential.username=x-access-token pull origin'
alias gpush='git -c credential.username=x-access-token push origin'
gclone() {
  git -c credential.helper= clone "$@"
}
