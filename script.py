import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


def get_candidates(num_candidates: int):
    """
    Get candidate names from the user.

    Parameters:
    - num_candidates (int): The number of candidates.

    Returns:
    - list: List of candidate names.
    """

    name_candidates = []

    # Prompt the user for each candidate's name
    print("Please enter the candidate names (press enter after each name)\n")
    for i in range(num_candidates):
        name_candidates.append(input(f"\nCandidate n°{i + 1} : "))

    print("\n\nYou will refer to the candidates by their numbers")
    return name_candidates


def get_votes(num_candidates: int):
    """
    Get votes from users and create a matrix of duel counts.

    Parameters:
    - num_candidates (int): The number of candidates.

    Returns:
    - numpy.ndarray: Matrix representing duel counts.
    """

    # Get the number of voters
    num_voters = int(input("\nHow many voters are there : "))
    # Initialize a matrix to store duel counts
    duel_counts = np.zeros((num_candidates, num_candidates))

    print(
        "For each voter, you will give his vote by order according to the candidate number"
    )
    for i in range(num_voters):
        print(f"\n\nVoter n°{i + 1} choice : ")
        vote = []
        # Collect votes for each candidate
        for j in range(num_candidates):
            while True:
                choice = int(input(f"\nChoice n°{j + 1} : ")) - 1
                # Check if the candidate has already been selected
                if choice not in vote:
                    vote.append(choice)
                    break
                else:
                    print(
                        "You have already selected this candidate. Please choose another"
                    )

        # Update duel counts based on the votes in real-time
        # Compute victory counts - defeats counts
        for m in range(num_candidates - 1):
            for n in range(m + 1, num_candidates):
                duel_counts[vote[m], vote[n]] += 1
                duel_counts[vote[n], vote[m]] -= 1

    return duel_counts


def condorcet(duel_counts: np.ndarray):
    """
    Compute the Condorcet matrix based on duel counts.

    Parameters:
    - duel_counts (numpy.ndarray): Matrix representing duel counts.

    Returns:
    - numpy.ndarray: Condorcet matrix.
    """

    # Initialize Condorcet matrix with zeros
    condorcet_matrix = np.zeros(duel_counts.shape)
    # Create a temporary matrix for processing
    temp_matrix = np.copy(duel_counts)

    # Continue the process until there are no more duels to check
    while np.max(temp_matrix) > 0:
        # Find the index of the duel with the highest number of encounter
        max_index = np.unravel_index(
            np.argmax(temp_matrix, axis=None), temp_matrix.shape
        )
        # Update the Condorcet matrix and mark the duel as resolved
        # Remove it from duel counts (in temporary matrix)
        condorcet_matrix[max_index], temp_matrix[max_index] = 1, 0

        try:
            # Attempt to find a cycle in the directed graph
            _ = nx.find_cycle(nx.DiGraph(condorcet_matrix, orientation="original"))
            # If a cycle is found, undo the last resolution
            # to avoid equally ranked winners at the end
            condorcet_matrix[max_index] = 0
        except nx.exception.NetworkXNoCycle:
            pass

    return condorcet_matrix


def plot_graph(
    adjacency_matrix: np.ndarray, node_names: list, weight_matrix: np.ndarray
):
    """
    Plot a directed graph based on the given adjacency matrix, node names, and weight matrix.

    Parameters:
    - adjacency_matrix (numpy.ndarray): Adjacency matrix representing the graph.
    - node_names (list): List of node names.
    - weight_matrix (numpy.ndarray): Weight matrix for the edges.

    Returns:
    - networkx.DiGraph: The created directed graph.
    """

    # Create a directed graph from the adjacency matrix
    graph = nx.DiGraph(adjacency_matrix)

    # Define dictionaries for nodes and edge weights
    labels = {i: nom for i, nom in enumerate(node_names)}
    weights = {
        (i, j): weight_matrix[i, j]
        for i, row in enumerate(weight_matrix)
        for j, value in enumerate(row)
        if value != 0
    }

    # Set up the layout for better visualization
    disposition = nx.spring_layout(graph)
    # Draw the graph (with labels and edge labels)
    nx.draw(
        graph,
        disposition,
        with_labels=False,
        arrowsize=20,
        node_size=700,
        node_color="skyblue",
    )
    nx.draw_networkx_labels(graph, disposition, labels=labels, font_size=15)
    nx.draw_networkx_edge_labels(
        graph, disposition, edge_labels=weights, font_color="red"
    )
    plt.show()

    return graph


def get_winner(directed_graph: nx.DiGraph):
    """
    Get the winner node in a Condorcet graph.

    Parameters:
    - directed_graph (networkx.DiGraph): Directed graph.

    Returns:
    - Node: The winner node.
    """

    winner = None

    for node in directed_graph.nodes():
        # Check if the node has no incoming edges (no predecessors)
        # Exit the loop once the winner is found
        if not any(directed_graph.predecessors(node)):
            winner = node
            break

    return winner


def main():
    """
    Main function to execute the Condorcet method.
    """

    print("\nStarting Condorcet method")

    num_candidates = int(input("\n\nHow many candidates are there : "))
    name_candidates = get_candidates(num_candidates)

    duel_counts = get_votes(num_candidates)
    condorcet_matrix = condorcet(duel_counts)

    # Plot Condorcet graph with duel encountered counts
    print("\n\nCondorcet graph :\n")
    condorcet_graph = plot_graph(
        condorcet_matrix, name_candidates, condorcet_matrix * duel_counts
    )
    # Output the name of the winner
    print(
        "\n\nThe winner, as determined by the Condorcet method, is : ",
        name_candidates[get_winner(condorcet_graph)],
    )


if __name__ == "__main__":
    main()
