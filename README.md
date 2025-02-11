# Automated Helm Chart Generator
This is a relatively simplistic Python app to simplify creating a Helm Chart more easily.

Keep in mind, this is fairly opinionated and simplistic in it's implementation. This is on purpose. This largely developed for my own use rather than general applicability.

## Getting Started
In general, there are 3 steps to run this automatation: 
1. Run the appropriate installer script (technically this isn't required as you could just run the Python script directly but is for convenience)
2. Create and customize a `input.json` file that has the inputs for the script
3. Run the script

### On Windows
Run the followng
```PowerShell
.\install.ps1
```

Next copy the `input.example.json` into the folder you want (replacing `<Folder for Helm Chart>` with the appropriate path) and rename it `input.json`. You'll also probably want to customize this file (though not technically required)
```PowerShell
Copy-Item input.example.json <Folder for Helm Chart>\input.json
```

Then in the directory you want
```PowerShell
create-helm-chart
```

### On Mac/Linux (Uses Bash)
Run the followng
```sh
./install.sh
```

Next copy the `input.example.json` into the folder you want (replacing `<Folder for Helm Chart>` with the appropriate path) and rename it `input.json`. You'll also probably want to customize this file (though not technically required)
```sh
cp ./input.example.json <Folder for Helm Chart>/input.json
```

Then in the directory you want
```sh
create-helm-chart
```