from abc import ABC, abstractmethod
import itertools

from opoly.statements import ForLoopStatement
from opoly.indexes import IndexDescriptor, IndexDescriptorType, IndexSet
from opoly.modules.checker import (
    extract_loop_indexes,
    get_inner_loop_statements,
    prune_expressions,
    divide_assignments,
    divide_variable_expressions_by_name,
    get_indexed_variable_simple_indexes,
    get_indexed_variable_index_constants_with_sign
)


class LoopDependenciesDetector():

    @abstractmethod
    def extract_dependencies(self, loop: ForLoopStatement) -> tuple[IndexSet]:
        pass


class LamportLoopDependenciesDetector(LoopDependenciesDetector):

    def generate_dependencies_from_couples(
        self,
        couples,
        indexes,
        indexes_pos_lookup,
        couples_index_pos_lookup
    ) -> list[IndexSet]:
        deps = []
        for gen1, gen2 in couples:
            gen1_consts = get_indexed_variable_index_constants_with_sign(gen1)
            gen2_consts = get_indexed_variable_index_constants_with_sign(gen2)
            dep_vector = tuple(c1.value - c2.value for c1,
                               c2 in zip(gen1_consts, gen2_consts))
            index_descriptors = [None] * len(indexes)
            for index in indexes:
                if index.name in couples_index_pos_lookup:  # pylint: disable=no-member
                    index_descriptors[indexes_pos_lookup[index.name]] = IndexDescriptor(  # pylint: disable=no-member
                        IndexDescriptorType.CONSTANT, value=dep_vector[
                            couples_index_pos_lookup[index.name]]  # pylint: disable=no-member
                    )
                else:
                    index_descriptors[indexes_pos_lookup[index.name]] = IndexDescriptor(  # pylint: disable=no-member
                        IndexDescriptorType.ANY
                    )
            deps.append(IndexSet(index_descriptors))
        return deps

    def extract_dependencies(self, loop: ForLoopStatement) -> tuple[IndexSet]:
        indexes = extract_loop_indexes(loop)
        inner_statements = get_inner_loop_statements(loop)
        lefts, rights = divide_assignments(inner_statements)
        generations, uses = prune_expressions(lefts, rights)
        uses = tuple(filter(lambda use: not use.is_simple(), uses))

        # Check variable indexes
        generations_by_name = divide_variable_expressions_by_name(generations)
        uses_by_name = divide_variable_expressions_by_name(uses)

        # Create index position lookup
        index_pos_lookup = {}
        for pos, index in enumerate(indexes):
            index_pos_lookup[index.name] = pos

        # Generate write-write dependencies
        write_write_index_sets = []
        for _, same_name_generations in generations_by_name.items():
            gen_indexes = get_indexed_variable_simple_indexes(
                same_name_generations[0])
            # Create gen index position lookup
            gen_index_pos_lookup = {}
            for pos, gen_index in enumerate(gen_indexes):
                gen_index_pos_lookup[gen_index.name] = pos
            # Create dependency index set between gen1 and gen2
            write_write_index_sets.extend(self.generate_dependencies_from_couples(
                itertools.product(same_name_generations,
                                  same_name_generations),
                indexes,
                index_pos_lookup,
                gen_index_pos_lookup
            ))

        # Generate write-read dependencies
        write_read_index_sets = []
        for var_name in generations_by_name.keys():
            gen_indexes = get_indexed_variable_simple_indexes(
                generations_by_name[var_name][0])
            # Create gen index position lookup
            gen_index_pos_lookup = {}
            for pos, gen_index in enumerate(gen_indexes):
                gen_index_pos_lookup[gen_index.name] = pos

            # Create dependency index set between gen1 and gen2
            gens_uses = itertools.product(
                generations_by_name[var_name], uses_by_name[var_name])
            uses_gens = itertools.product(
                uses_by_name[var_name], generations_by_name[var_name])
            write_read_index_sets.extend(self.generate_dependencies_from_couples(
                itertools.chain(gens_uses, uses_gens),
                indexes,
                index_pos_lookup,
                gen_index_pos_lookup
            ))

        # Eliminate equalities
        index_sets = set(list(write_write_index_sets) +
                         list(write_read_index_sets))
        # Expand sets
        expanded_index_sets = []
        for index_set in index_sets:
            expanded_index_sets.extend(index_set.extract_positives())
        # Convert sets to positive
        positive_sets = tuple(
            map(lambda x: x.to_converted(), expanded_index_sets))
        return positive_sets
